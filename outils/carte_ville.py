"""Prépare les données de la carte 3D de la ville (Aubagne, La Penne, La Valentine).

Lancé automatiquement par GitHub au moment de la publication du site (voir .github/workflows/pages.yml).
Entrée : la zone d'Aubagne extraite du fichier OpenStreetMap de la région PACA (Geofabrik),
         convertie par osmium en GeoJSON (une entité par ligne).
Relief : tuiles d'altitude publiques « Terrarium » (AWS).
Sortie : un seul fichier compact, en mètres autour du centre de la carte : prototype/carte/ville.json

Usage : python3 outils/carte_ville.py zone.geojsonseq prototype/carte/ville.json
"""
import base64, io, json, math, os, re, struct, sys, urllib.request

# zone couverte (sud, ouest, nord, est)
S, W, N, E = 43.250, 5.470, 43.345, 5.650
LAT0, LON0 = (S + N) / 2, (W + E) / 2
KX = 111320 * math.cos(math.radians(LAT0))
KZ = 110540
UA = {"User-Agent": "shin-carte/1.0 (jeu entre amis, generation unique)"}


def xz(lon, lat):
    """Longitude/latitude -> mètres (x vers l'est, z vers le sud)."""
    return round((lon - LON0) * KX, 1), round(-(lat - LAT0) * KZ, 1)


def lonlat(x, z):
    return LON0 + x / KX, LAT0 - z / KZ


TAILLE = (round((E - W) * KX), round((N - S) * KZ))


# ---------- bâtiments ----------
def nombre(v):
    m = re.match(r"\s*([0-9]+(?:[.,][0-9]+)?)", v or "")
    return float(m.group(1).replace(",", ".")) if m else None


GENRES = ["maison", "immeuble", "industrie", "commerce", "public", "religieux", "annexe", "autre"]


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


def hauteur(t, g):
    h = nombre(t.get("height"))
    if h and 2 <= h <= 150:
        return h
    n = nombre(t.get("building:levels"))
    if n and 0 < n < 50:
        return round(n * 3.1 + 1, 1)
    return HAUTEUR_DEFAUT[g]


def plat(points):
    pts = [xz(p["lon"], p["lat"]) for p in points if p]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    out = []
    for x, z in pts:
        out += [x, z]
    return out


# ---------- routes, eau, sols ----------
ROUTES = ["autoroute", "principale", "rue", "petite", "chemin"]


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


# ---------- relief ----------
def relief(pas=20):
    z = 13
    n = 2 ** z

    def tuile(lon, lat):
        x = (lon + 180) / 360 * n
        y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
        return x, y

    x0, y0 = tuile(W, N)
    x1, y1 = tuile(E, S)
    tx0, ty0, tx1, ty1 = int(x0), int(y0), int(x1), int(y1)
    from PIL import Image
    mos = {}
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{tx}/{ty}.png"
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                mos[(tx, ty)] = Image.open(io.BytesIO(r.read())).convert("RGB").load()

    def alt_px(px, py):
        tx, ty = int(px // 256), int(py // 256)
        tx, ty = min(max(tx, tx0), tx1), min(max(ty, ty0), ty1)
        ix, iy = min(255, max(0, int(px - tx * 256))), min(255, max(0, int(py - ty * 256)))
        r, g, b = mos[(tx, ty)][ix, iy]
        return r * 256 + g + b / 256 - 32768

    def alt(lon, lat):
        px, py = tuile(lon, lat)
        px, py = px * 256 - 0.5, py * 256 - 0.5
        ix, iy = math.floor(px), math.floor(py)
        fx, fy = px - ix, py - iy
        a, b = alt_px(ix, iy), alt_px(ix + 1, iy)
        c, d = alt_px(ix, iy + 1), alt_px(ix + 1, iy + 1)
        return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

    nx, nz = TAILLE[0] // pas + 1, TAILLE[1] // pas + 1
    vals = []
    for j in range(nz):
        for i in range(nx):
            lon, lat = lonlat(-TAILLE[0] / 2 + i * pas, -TAILLE[1] / 2 + j * pas)
            vals.append(max(-3000, min(30000, round(alt(lon, lat) * 10))))
    data = base64.b64encode(struct.pack(f"<{len(vals)}h", *vals)).decode()
    return {"nx": nx, "nz": nz, "pas": pas, "dm": data}


LIEUX = ("suburb", "quarter", "neighbourhood", "hamlet", "locality", "village")


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip().lstrip("\x1e")
            if ligne:
                yield json.loads(ligne)


def ligne_xz(coords):
    return [v for lon, lat in coords for v in xz(lon, lat)]


def anneau_xz(ring):
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring = ring[:-1]
    return ligne_xz(ring)


def main(entree, sortie):
    print("Relief…", flush=True)
    dem = relief()
    print("Lecture d'OpenStreetMap…", flush=True)
    batiments, routes, rails, rivieres, sols, communes, lieux = [], [], [], [], [], {}, []
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
                lieux.append([t["name"], t["place"]] + list(xz(*c)))
        elif "building" in t and t.get("building") != "no":
            gen = genre_batiment(t)
            for p in polys:
                pts = anneau_xz(p[0])
                if len(pts) >= 6:
                    batiments.append([hauteur(t, gen), GENRES.index(gen)] + pts)
        elif t.get("boundary") == "administrative":
            nom = t.get("name", "")
            if polys and ((t.get("admin_level") == "8" and nom in ("Aubagne", "La Penne-sur-Huveaune")) or nom == "La Valentine"):
                communes[nom] = [anneau_xz(p[0]) for p in polys]
        elif "highway" in t:
            cl = classe_route(t["highway"])
            if cl:
                pont = 1 if t.get("bridge") not in (None, "no") else (-1 if t.get("tunnel") not in (None, "no") else 0)
                for l in lignes:
                    if len(l) > 1:
                        routes.append([ROUTES.index(cl), pont] + ligne_xz(l))
        elif t.get("railway") == "rail" and t.get("tunnel") in (None, "no"):
            for l in lignes:
                rails.append(ligne_xz(l))
        elif t.get("waterway") in ("river", "stream", "canal") and typ in ("LineString", "MultiLineString"):
            large = {"river": 12, "canal": 6, "stream": 3}[t["waterway"]]
            for l in lignes:
                rivieres.append([large] + ligne_xz(l))
        else:
            sol = type_sol(t)
            if sol:
                for p in polys:
                    pts = anneau_xz(p[0])
                    if len(pts) >= 6:
                        sols.append([SOLS.index(sol)] + pts)
    print(f"  {len(batiments)} bâtiments, {len(routes)} routes, {len(sols)} zones, {len(rivieres)} cours d'eau, "
          f"{len(lieux)} lieux-dits, communes : {list(communes)}", flush=True)
    if not batiments or "Aubagne" not in communes:
        raise RuntimeError("Données incomplètes : pas de bâtiments ou pas de commune d'Aubagne")

    out = {"taille": TAILLE, "origine": [LON0, LAT0], "kx": KX, "kz": KZ, "relief": dem,
           "genres": GENRES, "batiments": batiments, "classes": ROUTES, "routes": routes, "rails": rails,
           "rivieres": rivieres, "typesSol": SOLS, "sols": sols, "communes": communes, "lieux": lieux,
           "source": "© les contributeurs d'OpenStreetMap (ODbL) ; relief : Terrarium / Mapzen (AWS)"}
    tmp = sortie + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
    os.replace(tmp, sortie)
    print(f"Écrit : {sortie} ({os.path.getsize(sortie) // 1024} Ko)", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "prototype/carte/ville.json")
