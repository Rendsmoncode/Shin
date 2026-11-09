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

## Étape B : vraies couleurs — faite (à vérifier sur le site)
- Photos aériennes drapées sur le relief, chargées par carrés selon la distance : vraies couleurs des routes, des champs et de la végétation.
- La même photo projetée sur chaque toit : vraie couleur des toits.
- Façades : matériau des murs de la BD TOPO, couleur OSM si elle existe, sinon palette d'Aubagne (ocre, crème, rosé, blanc cassé).

Réalisé : la page charge elle-même les photos IGN (WMTS `ORTHOIMAGERY.ORTHOPHOTOS`, `data.geopf.fr/wmts`, grille `PM`) : une photo de toute la zone (zoom 15, environ 3,7 m), puis par carré de 500 m selon la distance : zoom 19 (environ 26 cm) à moins de 650 m, zoom 18 (environ 53 cm) jusqu'à 1,5 km, zoom 16 (environ 1,7 m) jusqu'à 3,6 km. Les tuiles sont recollées dans une image alignée sur la carte, puis projetées d'en haut sur le sol, les routes, les rivières, les tabliers de pont et les toits (bâtiments rangés par carré). Les quartiers des joueurs restent teintés et les fortes pentes restent en roche. Si l'IGN ne répond pas, la carte peinte et les toits colorés (matériau BD TOPO ou `roof:colour` OSM) restent affichés. Façades : matériau des murs BD TOPO, `building:colour` OSM (ajouté par `outils/carte_ville.py`), palette d'Aubagne. La publication garde l'ancienne carte si la régénération échoue (empreinte dans `relief/empreinte.txt`).

## Étape C : détails — faite (à vérifier sur le site)
- Toits en pente en tuiles sur les maisons, toits plats sur les immeubles et l'industrie (BD TOPO et OSM).
- Fenêtres étage par étage et portes au rez-de-chaussée.
- Arbres sur les zones boisées et sur les arbres OSM (alignements, arbres isolés), teintés avec la couleur de la photo à leur emplacement.

Réalisé (`prototype/carte/index.html`, et `outils/carte_ville.py` pour les données) :
- **Toits** : forme lue dans OpenStreetMap (`roof:shape`, ajoutée aux bâtiments BD TOPO), sinon déduite de l'écart gouttière-faîte de la BD TOPO, du matériau de toiture, du genre et de la taille du bâtiment, et de la photo (beaucoup de tuiles rouges → toit en pente ; toit gris sans tuiles ni pente connue → toit-terrasse). Deux pans pour les bâtiments allongés, quatre pans sinon, un pan pour les petites annexes ; faîtage dans le sens du grand côté du rectangle qui enveloppe le bâtiment ; débord de 40 cm sur les bâtiments presque rectangulaires ; murs coupés pour monter jusqu'au toit (pignons). Les toits-terrasses des immeubles ont un acrotère.
- **Tuiles** : texture de tuiles canal (bombées et creuses en alternance) dessinée par la page, teintée par la couleur du toit lue sur la photo (sinon matériau BD TOPO). Elle prend le relais de la photo à moins de 260 m de la caméra (la photo reprend au-delà de 620 m), ce qui corrige le décalage du toit photographié.
- **Variété des toits** (retour de l'utilisateur : « tous identiques ») : chaque toit a sa teinte et sa graine : tuiles dépareillées, usure, taches et coulures dans le sens de la pente, lichen, taille des tuiles ; faîtage et arêtiers marqués avec leur mortier, tuiles de rive plus sombres, épaisseur du toit au bord du débord, cheminée enduite sur la plupart des maisons.
- **Murs** : couleur lue sur la photo fine (zoom 18 ou 19) juste autour du bâtiment (la façade y apparaît souvent de biais : couleurs claires, peu saturées, sans végétation ni ombre), mêlée à la palette ; sinon matériau BD TOPO, couleur OSM, palette d'Aubagne. Le carré est reconstruit quand sa photo fine arrive.
- **Façades** : fenêtres à chaque étage (nombre d'étages BD TOPO, sinon hauteur d'étage selon le genre), encadrements, appuis, volets de couleurs provençales sur les maisons et la plupart des immeubles, porte sur le plus long mur, vitrines et enseignes au rez-de-chaussée des commerces, bandeau de fenêtres et grand portail pour l'industrie, hautes fenêtres pour les lieux de culte, soubassement plus sombre. Les détails s'effacent de loin pour éviter le scintillement.
- **Arbres** : arbres isolés (`natural=tree`) et alignements (`natural=tree_row`, un arbre tous les 8 m) d'OpenStreetMap ajoutés aux zones boisées ; tous teintés par la photo à leur emplacement quand elle ressemble à de la végétation.
- **Zoom limité** : la caméra s'arrête à 140 m (230 m si l'IGN ne donne que le zoom 18) et se redresse de près, pour ne pas descendre là où la photo devient floue.

Limites annoncées à l'utilisateur : voitures et ombres présentes sur les photos, léger décalage des toits photographiés des grands immeubles, façades crédibles mais pas exactes.
