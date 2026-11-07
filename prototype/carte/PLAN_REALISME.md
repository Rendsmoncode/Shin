# Plan : rendre la carte 3D d'Aubagne fidèle à la réalité

Validé par l'utilisateur. **Ne pas réduire la qualité.** Faire **une étape par session** (nouvelle conversation à chaque fois), en une seule passe, sans test dans la session (l'utilisateur teste sur le site), et vérifier la publication GitHub **une seule fois**.

État actuel : `prototype/carte/index.html` (three.js 0.147) affiche `ville.json`, produit par `outils/carte_ville.py` dans la publication GitHub (`.github/workflows/pages.yml`) à partir de l'extrait OpenStreetMap PACA de Geofabrik (osmium) et du relief Terrarium (environ 30 m), avec un cache par empreinte du script. Les hauteurs des bâtiments sont estimées et le sol est peint en aplats de couleur.

Sources gratuites (IGN, Licence ouverte, citer « IGN ») via la Géoplateforme `data.geopf.fr` : vérifier d'abord qu'elles répondent depuis GitHub Actions.
- **RGE ALTI** : relief au sol de 1 à 5 m.
- **BD TOPO** (`BDTOPO_V3:batiment` en WFS) : contour, `hauteur`, `altitude_minimale_sol`, `altitude_maximale_toit`, `nombre_d_etages`, matériaux des murs et de la toiture.
- **Orthophotos** (WMTS `ORTHOIMAGERY.ORTHOPHOTOS`) : photos aériennes à 20 cm.

## Étape A : relief et niveaux — faite (à vérifier sur le site)
- Relief RGE ALTI précis. Ville découpée en carrés d'environ 500 m, avec un niveau de détail selon la distance (haute précision près de la caméra).
- Murs de soutènement (`barrier=retaining_wall` dans OSM) construits en pierre à la hauteur du ressaut. Les ressauts nets sans mur recensé sont coloriés en roche ou pierre.
- Bâtiments BD TOPO à leur vraie hauteur, posés selon l'altitude de leur pied et de leur toit, sans flotter ni s'enfoncer.
- Ponts à plat, tunnels cachés, routes qui suivent le relief.

Réalisé : `outils/carte_ville.py` lit le relief RGE ALTI (WMS `ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES`, valeurs brutes) tous les 2 m et l'écrit en images dans `prototype/carte/relief/` (`global.png` à 10 m, `t_i_j.png` par carré de 500 m) ; bâtiments BD TOPO par WFS (OSM en secours carré par carré) ; ponts chaînés d'une culée à l'autre. La page choisit 5 niveaux de détail (2, 4, 10, 20, 50 m) selon la distance, pose routes, rivières et murs sur le relief affiché, colorie en roche les pentes de plus de 40° environ. Si l'IGN ne répond pas depuis GitHub, le journal de publication l'indique et le relief Terrarium est utilisé.

## Étape B : vraies couleurs
- Photos aériennes drapées sur le relief, chargées par carrés selon la distance : vraies couleurs des routes, des champs et de la végétation.
- La même photo projetée sur chaque toit : vraie couleur des toits.
- Façades : matériau des murs de la BD TOPO, couleur OSM si elle existe, sinon palette d'Aubagne (ocre, crème, rosé, blanc cassé).

## Étape C : détails
- Toits en pente en tuiles sur les maisons, toits plats sur les immeubles et l'industrie (BD TOPO et OSM).
- Fenêtres étage par étage et portes au rez-de-chaussée.
- Arbres sur les zones boisées et sur les arbres OSM (alignements, arbres isolés), teintés avec la couleur de la photo à leur emplacement.

Limites annoncées à l'utilisateur : voitures et ombres présentes sur les photos, léger décalage des toits photographiés des grands immeubles, façades crédibles mais pas exactes.
