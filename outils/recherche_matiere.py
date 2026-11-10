"""Cherche des images anciennes libres de droits sur Wikimedia Commons (recherches listées dans
outils/recherche_matiere.txt) et les télécharge dans prototype/identite/matiere/recherche/.
Lancé par GitHub (.github/workflows/recherche-matiere.yml) : le serveur de Claude est bloqué par Wikimedia."""
import json, os, re, time, urllib.parse, urllib.request
UA = {"User-Agent": "ShinPrototype/0.1 (github.com/Rendsmoncode/Shin)"}
LIBRES = ("public domain", "pd", "cc0", "no restrictions", "cc by", "cc-by")
def get(url):
    for essai in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception as e:
            print("  nouvel essai", essai, e); time.sleep(5 + 5 * essai)
    return None
dossier = "prototype/identite/matiere/recherche"
os.makedirs(dossier, exist_ok=True)
index = []
for ligne in open("outils/recherche_matiere.txt", encoding="utf-8"):
    ligne = ligne.strip()
    if not ligne or ligne.startswith("#"): continue
    cle, requete = ligne.split("|", 1)
    p = {"action": "query", "generator": "search", "gsrsearch": "filetype:bitmap " + requete, "gsrnamespace": 6,
         "gsrlimit": 12, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 960, "format": "json"}
    brut = get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p))
    if not brut: continue
    pages = sorted(json.loads(brut).get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 0))
    n = 0
    for pg in pages:
        ii = pg.get("imageinfo", [{}])[0]; m = ii.get("extmetadata", {})
        lic = m.get("LicenseShortName", {}).get("value", "")
        if not any(l in lic.lower() for l in LIBRES) or ii.get("width", 0) < 600: continue
        n += 1; nom = f"{cle}_{n}.jpg"
        donnees = get(ii.get("thumburl") or ii["url"])
        if not donnees: continue
        open(os.path.join(dossier, nom), "wb").write(donnees)
        auteur = re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", ""))[:120]
        index.append({"fichier": nom, "titre": pg["title"][5:], "licence": lic, "auteur": auteur, "page": ii.get("descriptionurl")})
        print(nom, lic, pg["title"][5:][:70])
        time.sleep(1)
        if n >= 6: break
    time.sleep(3)
json.dump(index, open(os.path.join(dossier, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
