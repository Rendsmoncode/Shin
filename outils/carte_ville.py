"""Prépare les données de la carte 3D de la ville (Aubagne, La Penne, La Valentine).

Lancé automatiquement par GitHub au moment de la publication du site (voir .github/workflows/pages.yml).
Entrées :
- la zone d'Aubagne extraite du fichier OpenStreetMap de la région PACA (Geofabrik), convertie par osmium
  en GeoJSON (une entité par ligne) : routes, rivières, sols, murs de soutènement, quartiers ;
- le relief IGN RGE ALTI (1 à 5 m) via la Géoplateforme (WMS, valeurs d'altitude brutes), rééchantillonné
  tous les 2 m ; secours : tuiles publiques « Terrarium » (environ 30 m) là où l'IGN ne répond pas ;
- les bâtiments IGN BD TOPO (WFS) avec leurs vraies altitudes de pied et de toit ; secours : OpenStreetMap ;
  couleurs des façades et des toits d'OpenStreetMap (building:colour, roof:colour) quand elles existent.
Les photos aériennes IGN ne sont pas préparées ici : la page les charge directement (WMTS), carré par carré.
Sorties (en mètres autour du centre de la carte) :
- prototype/carte/ville.json : tout sauf le relief fin ;
- prototype/carte/relief/ : le relief en images PNG (altitude codée en centimètres sur les 3 couleurs) :
  global.png (tous les 10 m) et un fichier t_i_j.png par carré de 500 m (tous les 2 m, avec 1 point de bord).

Usage : python3 outils/carte_ville.py zone.geojsonseq prototype/carte/ville.json
"""
import io, json, math, os, re, shutil, sys, time, unicodedata, urllib.parse, urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image

# zone couverte par OpenStreetMap et la BD TOPO (sud, ouest, nord, est)
S, W, N, E = 43.250, 5.470, 43.345, 5.650
LAT0, LON0 = (S + N) / 2, (W + E) / 2
KX = 111320 * math.cos(math.radians(LAT0))
KZ = 110540
UA = {"User-Agent": "shin-carte/2.0 (jeu entre amis, generation unique)"}

# relief : carrés de 500 m, un point tous les 2 m (un peu plus grand que la zone)
TUILE, PAS, NTX, NTZ = 500, 2, 30, 22
X0, Z0 = -NTX * TUILE / 2, -NTZ * TUILE / 2
NX, NZ = NTX * TUILE // PAS + 1, NTZ * TUILE // PAS + 1
GPAS = 10                      # relief global (vue de loin) : un point tous les 10 m
GK = GPAS // PAS
TAILLE = (NTX * TUILE, NTZ * TUILE)
DEM = None                     # altitudes (NZ x NX), rempli par releve()


def xz(lon, lat):
    """Longitude/latitude -> mètres (x vers l'est, z vers le sud)."""
    return round((lon - LON0) * KX, 1), round(-(lat - LAT0) * KZ, 1)


def lonlat(x, z):
    return LON0 + x / KX, LAT0 - z / KZ


def telecharger(url, essais=4, delai=180):
    err = None
    for k in range(essais):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=delai) as r:
                return r.read()
        except Exception as e:  # réseau ou serveur occupé : on réessaie
            err = e
            time.sleep(2 * 2 ** k)
    raise err


def nombre(v):
    if isinstance(v, (int, float)):
        return float(v)
    m = re.match(r"\s*(-?[0-9]+(?:[.,][0-9]+)?)", str(v or ""))
    return float(m.group(1).replace(",", ".")) if m else None


def sans_accent(s):
    return unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()


# ---------- relief ----------
WMS = [("https://data.geopf.fr/wms-r/wms", "ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES", "EPSG:4326"),
       ("https://data.geopf.fr/wms-r/wms", "ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES", "CRS:84"),
       ("https://data.geopf.fr/wms-r", "ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES", "EPSG:4326")]


def bloc_ign(base, couche, crs, x0, z0, nx, nz):
    """Altitudes IGN aux points x0 + i*PAS, z0 + j*PAS (tableau nz x nx, NaN si absent)."""
    lon0, lat1 = lonlat(x0 - PAS / 2, z0 - PAS / 2)
    lon1, lat0 = lonlat(x0 + (nx - .5) * PAS, z0 + (nz - .5) * PAS)
    bbox = f"{lat0},{lon0},{lat1},{lon1}" if crs == "EPSG:4326" else f"{lon0},{lat0},{lon1},{lat1}"
    q = urllib.parse.urlencode({"SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetMap", "LAYERS": couche,
                                "STYLES": "", "CRS": crs, "BBOX": bbox, "WIDTH": nx, "HEIGHT": nz,
                                "FORMAT": "image/x-bil;bits=32"})
    data = telecharger(base + "?" + q, essais=3)
    if len(data) != nx * nz * 4:
        raise ValueError(f"réponse inattendue ({len(data)} octets) : {data[:160]!r}")
    meilleur = None
    for ordre in ("<f4", ">f4"):
        a = np.frombuffer(data, ordre).reshape(nz, nx).astype(np.float32)
        ok = (a > -400) & (a < 4000)
        if meilleur is None or ok.sum() > meilleur[1].sum():
            meilleur = (a, ok)
    a, ok = meilleur
    a[~ok] = np.nan
    return a


def terrarium(dem):
    """Complète les trous du relief avec les tuiles Terrarium (AWS, environ 30 m)."""
    z = 13
    n = 2 ** z

    def tuile(lon, lat):
        lat = np.radians(lat)
        return (lon + 180) / 360 * n, (1 - np.log(np.tan(lat) + 1 / np.cos(lat)) / np.pi) / 2 * n

    (lo0, la1), (lo1, la0) = lonlat(X0, Z0), lonlat(X0 + TAILLE[0], Z0 + TAILLE[1])
    x0, y0 = tuile(np.float64(lo0), np.float64(la1))
    x1, y1 = tuile(np.float64(lo1), np.float64(la0))
    tx0, ty0, tx1, ty1 = int(x0), int(y0), int(x1), int(y1)
    mos = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256), np.float32)
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{tx}/{ty}.png"
            im = np.asarray(Image.open(io.BytesIO(telecharger(url))).convert("RGB"), np.float32)
            mos[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = \
                im[..., 0] * 256 + im[..., 1] + im[..., 2] / 256 - 32768
    H, Wm = mos.shape
    for j0 in range(0, NZ, 256):
        bloc = dem[j0:j0 + 256]
        trou = np.isnan(bloc)
        if not trou.any():
            continue
        jj, ii = np.nonzero(trou)
        lon, lat = lonlat(X0 + ii * PAS, Z0 + (jj + j0) * PAS)
        px, py = tuile(lon, lat)
        px = np.clip((px - tx0) * 256 - .5, 0, Wm - 1.001)
        py = np.clip((py - ty0) * 256 - .5, 0, H - 1.001)
        ix, iy = px.astype(int), py.astype(int)
        fx, fy = px - ix, py - iy
        v = (mos[iy, ix] * (1 - fx) + mos[iy, ix + 1] * fx) * (1 - fy) + (mos[iy + 1, ix] * (1 - fx) + mos[iy + 1, ix + 1] * fx) * fy
        bloc[jj, ii] = v


def releve():
    dem = np.full((NZ, NX), np.nan, np.float32)
    source = None
    choix = None
    for c in WMS:
        try:
            a = bloc_ign(*c, -50, -50, 51, 51)
            if np.isfinite(a).mean() > .9 and 0 < np.nanmean(a) < 1500:
                choix = c
                break
            print(f"  réponse IGN peu plausible ({c[0]}, {c[2]})", flush=True)
        except Exception as e:
            print(f"  IGN RGE ALTI indisponible ({c[0]}, {c[2]}) : {e}", flush=True)
    if choix:
        BL = 500
        blocs = [(i0, j0) for j0 in range(0, NZ, BL) for i0 in range(0, NX, BL)]

        def tache(b):
            i0, j0 = b
            nx, nz = min(BL, NX - i0), min(BL, NZ - j0)
            try:
                dem[j0:j0 + nz, i0:i0 + nx] = bloc_ign(*choix, X0 + i0 * PAS, Z0 + j0 * PAS, nx, nz)
                return True
            except Exception as e:
                print(f"  bloc de relief {b} : échec ({e})", flush=True)
                return False

        with ThreadPoolExecutor(4) as ex:
            ok = list(ex.map(tache, blocs))
        print(f"  IGN RGE ALTI : {sum(ok)}/{len(ok)} blocs reçus ({choix[0]}, {choix[2]})", flush=True)
        if sum(ok):
            source = "IGN RGE ALTI"
    trous = float(np.isnan(dem).mean())
    if trous > 0:
        print(f"  {trous:.1%} du relief complété avec Terrarium", flush=True)
        terrarium(dem)
        if source is None:
            source = "Terrarium / Mapzen (AWS)"
    return dem, source


def hauteurs(xs, zs):
    """Altitude du relief fin (interpolée) aux points donnés."""
    u = np.clip((np.asarray(xs, np.float64) - X0) / PAS, 0, NX - 1.001)
    v = np.clip((np.asarray(zs, np.float64) - Z0) / PAS, 0, NZ - 1.001)
    ix, iy = u.astype(int), v.astype(int)
    fu, fv = u - ix, v - iy
    return (DEM[iy, ix] * (1 - fu) + DEM[iy, ix + 1] * fu) * (1 - fv) + (DEM[iy + 1, ix] * (1 - fu) + DEM[iy + 1, ix + 1] * fu) * fv


def png_relief(a):
    v = np.clip(np.round((a.astype(np.float64) + 1000) * 100), 0, 2 ** 24 - 1).astype(np.uint32)
    rgb = np.stack([(v >> 16) & 255, (v >> 8) & 255, v & 255], -1).astype(np.uint8)
    return Image.fromarray(rgb, "RGB")


def ecrire_relief(dossier):
    os.makedirs(dossier)
    png_relief(DEM[::GK, ::GK]).save(os.path.join(dossier, "global.png"), compress_level=9)
    bord = np.pad(DEM, 1, mode="edge")
    k = TUILE // PAS
    for j in range(NTZ):
        for i in range(NTX):
            png_relief(bord[j * k:j * k + k + 3, i * k:i * k + k + 3]).save(os.path.join(dossier, f"t_{i}_{j}.png"), compress_level=9)


# ---------- bâtiments ----------
GENRES = ["maison", "immeuble", "industrie", "commerce", "public", "religieux", "annexe", "autre"]
CHAMPS_BAT = ["bas", "gouttiere", "faite", "genre", "etages", "murs", "toiture", "couleur", "couleur_toit", "forme_toit"]   # puis les points x, z
# forme du toit (OpenStreetMap roof:shape) : 0 inconnue, 1 plat, 2 deux pans, 3 quatre pans, 4 pyramide, 5 un pan
FORMES_TOIT = {"flat": 1, "round": 1, "dome": 1, "gabled": 2, "gambrel": 2, "saltbox": 2, "hipped": 3, "half-hipped": 3,
               "mansard": 3, "side_hipped": 3, "pyramidal": 4, "skillion": 5, "lean_to": 5}

COULEURS = []        # couleurs OpenStreetMap (texte brut) ; dans un bâtiment : 0 = aucune, k = COULEURS[k - 1]
_ICOUL = {}


def couleur(v):
    s = str(v or "").strip().lower()
    if not s or len(s) > 40:
        return 0
    if s not in _ICOUL:
        COULEURS.append(s)
        _ICOUL[s] = len(COULEURS)
    return _ICOUL[s]


def dans(x, z, flat):
    """Le point (x, z) est-il dans le polygone donné en liste plate x, z ?"""
    n, ok = len(flat) // 2, False
    for k in range(n):
        x1, z1, x2, z2 = flat[2 * k], flat[2 * k + 1], flat[2 * ((k + 1) % n)], flat[2 * ((k + 1) % n) + 1]
        if (z1 > z) != (z2 > z) and x < x1 + (z - z1) * (x2 - x1) / (z2 - z1):
            ok = not ok
    return ok


def poser_couleurs(batiments, colores):
    """Donne aux bâtiments BD TOPO la couleur OSM du bâtiment OSM dont le centre tombe dedans."""
    BH, C = len(CHAMPS_BAT), 100
    grille = defaultdict(list)
    for k, b in enumerate(batiments):
        xs, zs = b[BH::2], b[BH + 1::2]
        for i in range(int(min(xs) // C), int(max(xs) // C) + 1):
            for j in range(int(min(zs) // C), int(max(zs) // C) + 1):
                grille[i, j].append(k)
    n = 0
    for cx, cz, cm, ct, ft in colores:
        for k in grille.get((int(cx // C), int(cz // C)), ()):
            b = batiments[k]
            if dans(cx, cz, b[BH:]):
                if cm and not b[7]:
                    b[7] = cm
                if ct and not b[8]:
                    b[8] = ct
                if ft and not b[9]:
                    b[9] = ft
                n += 1
                break
    print(f"  couleurs et formes de toit OpenStreetMap : {n}/{len(colores)} posées sur la BD TOPO", flush=True)


def genre_batiment(t):
    b = t.get("building", "yes")
    if b in ("house", "detached", "semidetached_house", "terrace", "bungalow", "villa", "farm", "residential"):
        return "maison"
    if b in ("apartments", "dormitory", "hotel"):
        return "immeuble"
    if b in ("industrial", "warehouse", "factory", "hangar", "manufacture", "storage_tank"):
        return "industrie"
    if b in ("retail", "commercial", "supermarket", "office", "kiosk"):
        return "commerce"
    if b in ("school", "college", "university", "hospital", "public", "civic", "government", "train_station", "sports_hall", "stadium", "fire_station", "townhall"):
        return "public"
    if b in ("church", "chapel", "cathedral", "mosque", "temple", "religious", "synagogue"):
        return "religieux"
    if b in ("garage", "garages", "shed", "carport", "roof", "hut", "cabin", "greenhouse", "service", "barn", "stable", "farm_auxiliary"):
        return "annexe"
    return "autre"


HAUTEUR_DEFAUT = {"maison": 6.5, "immeuble": 15, "industrie": 9, "commerce": 7, "public": 10, "religieux": 14, "annexe": 3.2, "autre": 6}


def hauteur_osm(t, g):
    h = nombre(t.get("height"))
    if h and 2 <= h <= 150:
        return h
    n = nombre(t.get("building:levels"))
    if n and 0 < n < 50:
        return round(n * 3.1 + 1, 1)
    return HAUTEUR_DEFAUT[g]


def genre_bdtopo(p, aire):
    nat, us = sans_accent(p.get("nature")), sans_accent(p.get("usage_1"))
    et, lg = nombre(p.get("nombre_d_etages")) or 0, nombre(p.get("nombre_de_logements")) or 0
    if "eglise" in nat or "chapelle" in nat or "religieux" in us:
        return "religieux"
    if "residentiel" in us:
        return "immeuble" if et >= 3 or lg >= 4 else "maison"
    if "industriel" in us or "silo" in nat:
        return "industrie"
    if "commercial" in us:
        return "commerce"
    if "sportif" in us or nat in ("chateau", "monument", "tour, donjon", "arc de triomphe", "fort, blockhaus, casemate"):
        return "public"
    if "agricole" in us or "serre" in nat or "annexe" in us:
        return "annexe"
    if nat.startswith("industriel"):
        return "industrie"
    return "annexe" if aire < 25 else "autre"


def aire(pts):
    a = 0
    for k in range(len(pts)):
        (x1, z1), (x2, z2) = pts[k], pts[(k + 1) % len(pts)]
        a += x1 * z2 - x2 * z1
    return abs(a) / 2


def code(v):
    s = str(v or "").strip()
    return int(s) if s.isdigit() and len(s) <= 4 else 0


def enregistrement(pts, genre, sol=None, gout=None, faite=None, h=None, etages=0, murs=0, toit=0, coul=0, coul_toit=0, forme=0):
    """Bâtiment posé sur le relief : bas des murs sous le point le plus bas du terrain, toit à sa vraie altitude."""
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    hs = hauteurs(xs + [sum(xs) / len(xs)], zs + [sum(zs) / len(zs)])
    hmin, hmax, hmoy = float(hs.min()), float(hs.max()), float(hs.mean())
    if sol is None or abs(sol - hmin) > 8:
        sol = hmin
    bas = min(hmin, sol) - 1.5
    if gout is None or not (sol + 1.5 < gout < sol + 160):
        if h and 1.5 <= h <= 160:
            gout = sol + h
        elif etages and 0 < etages < 50:
            gout = sol + etages * 3.1 + 1
        else:
            gout = hmoy + HAUTEUR_DEFAUT[genre]
    gout = max(gout, hmax + 1.5)
    if faite is None or not (gout <= faite <= gout + 25):
        faite = gout
    flat = [v for p in pts for v in p]
    return [round(bas, 1), round(gout, 1), round(faite, 1), GENRES.index(genre), int(etages or 0), murs, toit, coul, coul_toit, forme] + flat


def batiments_bdtopo():
    """Bâtiments BD TOPO par carrés d'environ 1 km. Renvoie (enregistrements, carrés en échec en mètres)."""
    base = "https://data.geopf.fr/wfs/ows"
    DLON, DLAT = 0.0125, 0.009
    cases = [(W + i * DLON, S + j * DLAT, min(E, W + (i + 1) * DLON), min(N, S + (j + 1) * DLAT))
             for j in range(math.ceil((N - S) / DLAT - 1e-9)) for i in range(math.ceil((E - W) / DLON - 1e-9))]

    def tache(c):
        lo0, la0, lo1, la1 = c
        feats, debut = [], 0
        try:
            while True:
                q = urllib.parse.urlencode({"SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
                                            "TYPENAMES": "BDTOPO_V3:batiment", "OUTPUTFORMAT": "application/json",
                                            "SRSNAME": "EPSG:4326", "COUNT": 5000, "STARTINDEX": debut,
                                            "BBOX": f"{la0},{lo0},{la1},{lo1},urn:ogc:def:crs:EPSG::4326"})
                d = json.loads(telecharger(base + "?" + q))
                fs = d.get("features") or []
                feats += fs
                debut += len(fs)
                tot = d.get("numberMatched", d.get("totalFeatures"))
                if not fs or (isinstance(tot, int) and debut >= tot) or (not isinstance(tot, int) and len(fs) < 5000):
                    return c, feats
        except Exception as e:
            print(f"  BD TOPO : carré {c} en échec ({e})", flush=True)
            return c, None

    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(tache, cases))
    vus, out, echecs = set(), [], []
    for c, feats in res:
        if feats is None:
            (x0, z1), (x1, z0) = xz(c[0], c[1]), xz(c[2], c[3])
            echecs.append((x0, z0, x1, z1))
            continue
        for f in feats:
            p = f.get("properties") or {}
            ident = p.get("cleabs") or f.get("id")
            if ident in vus:
                continue
            vus.add(ident)
            if sans_accent(p.get("etat_de_l_objet")).startswith("en projet"):
                continue
            g = f.get("geometry") or {}
            polys = [g.get("coordinates")] if g.get("type") == "Polygon" else g.get("coordinates") or []
            for poly in polys:
                if not poly or len(poly[0]) < 4:
                    continue
                ring = poly[0][:-1] if poly[0][0] == poly[0][-1] else poly[0]
                inv = ring[0][0] > 30   # coordonnées données en latitude, longitude
                pts = [xz(c_[1], c_[0]) if inv else xz(c_[0], c_[1]) for c_ in ring]
                if len(pts) < 3:
                    continue
                a = aire(pts)
                genre = genre_bdtopo(p, a)
                out.append(enregistrement(pts, genre, sol=nombre(p.get("altitude_minimale_sol")),
                                          gout=nombre(p.get("altitude_minimale_toit")), faite=nombre(p.get("altitude_maximale_toit")),
                                          h=nombre(p.get("hauteur")), etages=nombre(p.get("nombre_d_etages")) or 0,
                                          murs=code(p.get("materiaux_des_murs")), toit=code(p.get("materiaux_de_la_toiture"))))
    print(f"  BD TOPO : {len(out)} bâtiments, {len(echecs)}/{len(cases)} carrés en échec", flush=True)
    return out, echecs


# ---------- routes, eau, sols ----------
ROUTES = ["autoroute", "principale", "rue", "petite", "chemin", "rail"]
LARGEUR = {"autoroute": 16, "principale": 10, "rue": 7, "petite": 4.5, "chemin": 2.2, "rail": 3}


def classe_route(h):
    if h in ("motorway", "motorway_link", "trunk", "trunk_link"):
        return "autoroute"
    if h in ("primary", "primary_link", "secondary", "secondary_link"):
        return "principale"
    if h in ("tertiary", "tertiary_link", "residential", "unclassified", "living_street", "road"):
        return "rue"
    if h in ("service",):
        return "petite"
    if h in ("footway", "path", "pedestrian", "cycleway", "steps", "track", "bridleway"):
        return "chemin"
    return None


SOLS = ["eau", "foret", "garrigue", "herbe", "champ", "vigne", "sport", "industriel", "residentiel", "parking", "roche", "cimetiere"]


def type_sol(t):
    n, l, le = t.get("natural"), t.get("landuse"), t.get("leisure")
    if n == "water" or l in ("reservoir", "basin"):
        return "eau"
    if n == "wood" or l == "forest":
        return "foret"
    if n in ("scrub", "heath"):
        return "garrigue"
    if n == "bare_rock" or l == "quarry":
        return "roche"
    if l in ("vineyard",):
        return "vigne"
    if l in ("farmland", "orchard", "allotments", "greenhouse_horticulture", "plant_nursery", "farmyard"):
        return "champ"
    if l in ("grass", "meadow", "recreation_ground", "village_green") or n == "grassland" or le in ("park", "garden", "golf_course"):
        return "herbe"
    if le in ("pitch", "stadium", "sports_centre"):
        return "sport"
    if l in ("industrial", "commercial", "retail", "railway", "construction", "brownfield", "military"):
        return "industriel"
    if l == "residential":
        return "residentiel"
    if l == "cemetery":
        return "cimetiere"
    if t.get("amenity") == "parking":
        return "parking"
    return None


def h_route(p, q, w):
    """Hauteur du terrain sous une route au point p (le plus haut sur toute la largeur)."""
    dx, dz = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dz) or 1
    nx, nz = -dz / L * w / 2, dx / L * w / 2
    return float(hauteurs([p[0], p[0] + nx, p[0] - nx], [p[1], p[1] + nz, p[1] - nz]).max())


def chainer_ponts(ponts, ancres):
    """Relie bout à bout les morceaux d'un même pont, pour qu'il reste à plat d'une culée à l'autre."""
    bouts = defaultdict(list)
    for k, (_, pts) in enumerate(ponts):
        bouts[pts[0]].append(k)
        bouts[pts[-1]].append(k)
    pris = [False] * len(ponts)
    out = []

    def prolonger(seq):
        while True:
            cle = seq[-1]
            if cle in ancres or len(bouts[cle]) != 2:
                return
            suite = [k for k in bouts[cle] if not pris[k]]
            if not suite:
                return
            k = suite[0]
            pris[k] = True
            p = ponts[k][1]
            seq.extend((p if p[0] == cle else p[::-1])[1:])

    for k, (cl, pts) in enumerate(ponts):
        if pris[k]:
            continue
        pris[k] = True
        seq = list(pts)
        prolonger(seq)
        seq.reverse()
        prolonger(seq)
        w = LARGEUR[ROUTES[cl]]
        ya, yb = h_route(seq[0], seq[1], w), h_route(seq[-1], seq[-2], w)
        out.append([cl, round(ya, 2), round(yb, 2)] + [v for p in seq for v in p])
    return out


LIEUX = ("suburb", "quarter", "neighbourhood", "hamlet", "locality", "village")


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip().lstrip("\x1e")
            if ligne:
                yield json.loads(ligne)


def pts_xz(coords):
    return [xz(lon, lat) for lon, lat, *_ in coords]


def anneau(ring):
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring = ring[:-1]
    return pts_xz(ring)


def plat(pts):
    return [v for p in pts for v in p]


def main(entree, sortie):
    global DEM
    print("Relief…", flush=True)
    DEM, src_relief = releve()
    print("Lecture d'OpenStreetMap…", flush=True)
    bat_osm, routes, ponts, ancres, rivieres, murs, sols, communes, lieux = [], [], [], set(), [], [], [], {}, []
    arbres, rangees = [], []   # arbres OpenStreetMap : isolés (natural=tree) et alignements (natural=tree_row)
    for f in lire(entree):
        t = f.get("properties") or {}
        g = f.get("geometry") or {}
        typ, c = g.get("type"), g.get("coordinates")
        if not c:
            continue
        polys = [c] if typ == "Polygon" else c if typ == "MultiPolygon" else []
        lignes = [c] if typ == "LineString" else c if typ == "MultiLineString" else [p[0] for p in polys]
        if typ == "Point":
            if t.get("place") in LIEUX and t.get("name"):
                lieux.append([t["name"], t["place"]] + list(xz(*c[:2])))
            elif t.get("natural") == "tree":
                x, z = xz(*c[:2])
                arbres += [round(x, 1), round(z, 1)]
        elif t.get("natural") == "tree_row":
            for l in lignes:
                if len(l) > 1:
                    rangees.append([round(v, 1) for v in plat(pts_xz(l))])
        elif t.get("barrier") == "retaining_wall" or t.get("wall") == "retaining_wall":
            for l in lignes:
                if len(l) > 1:
                    murs.append(plat(pts_xz(l)))
        elif "building" in t and t.get("building") != "no":
            gen = genre_batiment(t)
            for p in polys:
                pts = anneau(p[0])
                if len(pts) >= 3:
                    bat_osm.append((pts, gen, hauteur_osm(t, gen), couleur(t.get("building:colour")), couleur(t.get("roof:colour")),
                                    FORMES_TOIT.get(str(t.get("roof:shape", "")).strip().lower(), 0)))
        elif t.get("boundary") == "administrative":
            nom = t.get("name", "")
            if polys and ((t.get("admin_level") == "8" and nom in ("Aubagne", "La Penne-sur-Huveaune")) or nom == "La Valentine"):
                communes[nom] = [plat(anneau(p[0])) for p in polys]
        elif "highway" in t or t.get("railway") in ("rail", "light_rail", "tram"):
            cl = classe_route(t["highway"]) if "highway" in t else "rail"
            if cl:
                pont, tunnel = t.get("bridge") not in (None, "no"), t.get("tunnel") not in (None, "no")
                for l in lignes:
                    pts = pts_xz(l)
                    if len(pts) < 2:
                        continue
                    if pont and not tunnel:
                        ponts.append((ROUTES.index(cl), pts))
                        continue
                    ancres.update(pts)
                    if not tunnel:        # tunnels cachés
                        routes.append([ROUTES.index(cl)] + plat(pts))
        elif t.get("waterway") in ("river", "stream", "canal") and typ in ("LineString", "MultiLineString"):
            if t.get("tunnel") not in (None, "no"):
                continue                  # cours d'eau busés : cachés
            large = {"river": 12, "canal": 6, "stream": 3}[t["waterway"]]
            for l in lignes:
                if len(l) > 1:
                    rivieres.append([large] + plat(pts_xz(l)))
        else:
            sol = type_sol(t)
            if sol:
                for p in polys:
                    pts = anneau(p[0])
                    if len(pts) >= 3:
                        sols.append([SOLS.index(sol)] + plat(pts))
    ponts = chainer_ponts(ponts, ancres)

    print("Bâtiments BD TOPO…", flush=True)
    try:
        batiments, echecs = batiments_bdtopo()
    except Exception as e:
        print(f"  BD TOPO indisponible : {e}", flush=True)
        batiments, echecs = [], None
    if len(batiments) < 1000:
        batiments, echecs, src_bat = [], None, "OpenStreetMap"
    else:
        src_bat = "IGN BD TOPO"
    colores = []
    for pts, gen, h, cm, ct, ft in bat_osm:   # OpenStreetMap là où la BD TOPO n'a pas répondu
        cx, cz = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        if echecs is None or any(x0 <= cx < x1 and z0 <= cz < z1 for x0, z0, x1, z1 in echecs):
            batiments.append(enregistrement(pts, gen, h=h, coul=cm, coul_toit=ct, forme=ft))
        elif cm or ct or ft:
            colores.append((cx, cz, cm, ct, ft))
    if colores:
        poser_couleurs(batiments, colores)

    print(f"  {len(batiments)} bâtiments ({src_bat}), {len(routes)} routes, {len(ponts)} ponts, {len(murs)} murs de soutènement, "
          f"{len(sols)} zones, {len(rivieres)} cours d'eau, {len(arbres) // 2} arbres et {len(rangees)} alignements, "
          f"{len(lieux)} lieux-dits, communes : {list(communes)}", flush=True)
    if not batiments or "Aubagne" not in communes:
        raise RuntimeError("Données incomplètes : pas de bâtiments ou pas de commune d'Aubagne")

    dossier = os.path.join(os.path.dirname(sortie) or ".", "relief")
    print("Écriture du relief…", flush=True)
    shutil.rmtree(dossier + ".tmp", ignore_errors=True)
    ecrire_relief(dossier + ".tmp")
    out = {"taille": TAILLE, "origine": [LON0, LAT0], "kx": KX, "kz": KZ,
           "relief": {"tuile": TUILE, "pas": PAS, "nt": [NTX, NTZ], "x0": X0, "z0": Z0, "gpas": GPAS,
                      "gn": [(NX - 1) // GK + 1, (NZ - 1) // GK + 1], "dossier": "relief/", "source": src_relief},
           "genres": GENRES, "champsBat": CHAMPS_BAT, "couleursBat": COULEURS, "batiments": batiments, "classes": ROUTES, "largeurs": LARGEUR,
           "routes": routes, "ponts": ponts, "rivieres": rivieres, "murs": murs, "typesSol": SOLS, "sols": sols,
           "communes": communes, "lieux": lieux, "arbres": arbres, "rangees": rangees,
           "source": f"© les contributeurs d'OpenStreetMap (ODbL) ; relief : {src_relief} ; bâtiments : {src_bat}"}
    tmp = sortie + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
    shutil.rmtree(dossier, ignore_errors=True)
    os.replace(dossier + ".tmp", dossier)
    os.replace(tmp, sortie)
    print(f"Écrit : {sortie} ({os.path.getsize(sortie) // 1024} Ko) et {dossier}/ ({NTX * NTZ + 1} images)", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "prototype/carte/ville.json")
