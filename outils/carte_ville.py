"""Prépare les données de la carte 3D de la ville (Aubagne, La Penne, La Valentine).

Lancé automatiquement par GitHub au moment de la publication du site (voir .github/workflows/pages.yml).
Télécharge :
  - les bâtiments, routes, rivières, forêts, champs… depuis OpenStreetMap (service Overpass) ;
  - le relief depuis les tuiles d'altitude publiques « Terrarium » (AWS).
Écrit un seul fichier compact, en mètres autour du centre de la carte : prototype/carte/ville.json

Usage : python3 outils/carte_ville.py prototype/carte/ville.json
"""
import base64, io, json, math, os, re, struct, sys, time, urllib.parse, urllib.request

# zone couverte (sud, ouest, nord, est)
S, W, N, E = 43.250, 5.470, 43.345, 5.650
LAT0, LON0 = (S + N) / 2, (W + E) / 2
KX = 111320 * math.cos(math.radians(LAT0))
KZ = 110540
UA = {"User-Agent": "shin-carte/1.0 (jeu entre amis, generation unique)"}
SERVEURS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]


def xz(lon, lat):
    """Longitude/latitude -> mètres (x vers l'est, z vers le sud)."""
    return round((lon - LON0) * KX, 1), round(-(lat - LAT0) * KZ, 1)


def lonlat(x, z):
    return LON0 + x / KX, LAT0 - z / KZ


TAILLE = (round((E - W) * KX), round((N - S) * KZ))
BBOX = f"({S},{W},{N},{E})"


def overpass(requete, essais=2):
    data = urllib.parse.urlencode({"data": requete}).encode()
    for essai in range(essais):
        for s in SERVEURS:
            try:
                req = urllib.request.Request(s, data=data, headers=UA)
                with urllib.request.urlopen(req, timeout=400) as r:
                    return json.load(r)
            except Exception as e:  # serveur saturé : on essaie le suivant
                print(f"  {s} : {e}", flush=True)
        time.sleep(15)
    raise RuntimeError("OpenStreetMap ne répond pas")


def charger(corps, s=S, w=W, n=N, e=E, profondeur=0):
    """Télécharge une partie de la carte. Si c'est trop gros pour le serveur, on coupe la zone en 4 et on recommence."""
    bb = f"({s},{w},{n},{e})"
    q = f"[out:json][timeout:300][maxsize:1073741824];({corps.replace('BBOX', bb)});out tags geom;"
    try:
        return overpass(q)["elements"]
    except Exception:
        if profondeur >= 3:
            raise
        print(f"  trop gros : découpage en 4 (niveau {profondeur + 1})", flush=True)
        ms, mw = (s + n) / 2, (w + e) / 2
        res = {}
        for z in [(s, w, ms, mw), (s, mw, ms, e), (ms, w, n, mw), (ms, mw, n, e)]:
            for el in charger(corps, *z, profondeur + 1):
                res[(el["type"], el["id"])] = el
        return list(res.values())


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


def anneaux(rel):
    """Relie les morceaux extérieurs d'une relation en contours fermés (listes de points lon/lat)."""
    segs = [[(p["lon"], p["lat"]) for p in m["geometry"] if p] for m in rel.get("members", [])
            if m.get("type") == "way" and m.get("geometry") and m.get("role") != "inner"]
    segs = [s for s in segs if len(s) > 1]
    out = []
    while segs:
        ring = segs.pop(0)
        change = True
        while change and ring[0] != ring[-1]:
            change = False
            for i, s in enumerate(segs):
                if s[0] == ring[-1]:
                    ring = ring + s[1:]
                elif s[-1] == ring[-1]:
                    ring = ring + s[::-1][1:]
                elif s[-1] == ring[0]:
                    ring = s + ring[1:]
                elif s[0] == ring[0]:
                    ring = s[::-1] + ring[1:]
                else:
                    continue
                segs.pop(i)
                change = True
                break
        if len(ring) > 3 and ring[0] == ring[-1]:
            out.append(ring)
    return out


def plat_ll(ring):
    out = []
    for lon, lat in ring[:-1]:
        out += list(xz(lon, lat))
    return out


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


def main(sortie):
    print("Relief…", flush=True)
    dem = relief()
    print("Bâtiments…", flush=True)
    bat = charger('way["building"]BBOX;')
    batiments = []
    for e in bat:
        if e.get("type") != "way" or not e.get("geometry"):
            continue
        t = e.get("tags", {})
        g = genre_batiment(t)
        pts = plat(e["geometry"])
        if len(pts) >= 6:
            batiments.append([hauteur(t, g), GENRES.index(g)] + pts)
    print(f"  {len(batiments)} bâtiments", flush=True)

    elements = []
    parties = [
        ("Routes", 'way["highway"]BBOX;', True),
        ("Rivières et voies ferrées", 'way["railway"="rail"]BBOX;way["waterway"~"^(river|stream|canal)$"]BBOX;', True),
        ("Forêts et nature", 'way["natural"~"^(water|wood|scrub|heath|grassland|bare_rock)$"]BBOX;', True),
        ("Champs, parcs et zones", 'way["landuse"]BBOX;way["leisure"~"^(park|pitch|garden|golf_course|stadium|sports_centre)$"]BBOX;way["amenity"="parking"]BBOX;', True),
        ("Grandes zones naturelles", 'relation["natural"~"^(water|wood|scrub|heath)$"]BBOX;relation["landuse"~"^(forest|farmland|vineyard|residential|industrial|meadow|grass)$"]BBOX;', False),
        ("Communes", 'relation["boundary"="administrative"]["admin_level"="8"]["name"~"^(Aubagne|La Penne-sur-Huveaune)$"];relation["boundary"="administrative"]["name"="La Valentine"](43.28,5.44,43.34,5.53);', True),
        ("Lieux-dits", 'node["place"~"^(suburb|quarter|neighbourhood|hamlet|locality|village)$"]BBOX;', True),
    ]
    for nom, corps, obligatoire in parties:
        print(f"{nom}…", flush=True)
        try:
            els = charger(corps)
        except Exception as e:
            if obligatoire:
                raise
            print(f"  ignoré ({e})", flush=True)
            els = []
        print(f"  {len(els)} éléments", flush=True)
        elements += els
    routes, rails, rivieres, sols, communes, lieux = [], [], [], [], {}, []
    for e in elements:
        t = e.get("tags", {})
        if e["type"] == "node":
            if t.get("name"):
                lieux.append([t["name"], t.get("place", "")] + list(xz(e["lon"], e["lat"])))
            continue
        if e["type"] == "relation":
            if t.get("boundary") == "administrative":
                communes[t.get("name", "?")] = [plat_ll(r) for r in anneaux(e)]
                continue
            s = type_sol(t)
            if s:
                for r in anneaux(e):
                    sols.append([SOLS.index(s)] + plat_ll(r))
            continue
        geom = e.get("geometry")
        if not geom:
            continue
        if "highway" in t:
            c = classe_route(t["highway"])
            if c:
                pont = 1 if t.get("bridge") not in (None, "no") else (-1 if t.get("tunnel") not in (None, "no") else 0)
                routes.append([ROUTES.index(c), pont] + [v for p in geom for v in xz(p["lon"], p["lat"])])
        elif t.get("railway") == "rail":
            rails.append([v for p in geom for v in xz(p["lon"], p["lat"])])
        elif "waterway" in t:
            large = {"river": 12, "canal": 6, "stream": 3}[t["waterway"]]
            rivieres.append([large] + [v for p in geom for v in xz(p["lon"], p["lat"])])
        else:
            s = type_sol(t)
            if s and len(geom) > 3:
                sols.append([SOLS.index(s)] + plat(geom))
    print(f"  {len(routes)} routes, {len(sols)} zones, {len(rivieres)} cours d'eau, {len(lieux)} lieux-dits, communes : {list(communes)}", flush=True)

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
    main(sys.argv[1] if len(sys.argv) > 1 else "prototype/carte/ville.json")
