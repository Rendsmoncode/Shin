---
name: style-visuel
description: Style visuel du champ de bataille et de la carte du jeu (nom de code Shin). À utiliser dès que l'utilisateur demande un visuel du jeu à générer avec Gemini (Nano Banana) ou à traiter : soldats, troupes, cavaliers, archers, personnage sur le terrain, bâtiment, tente, quartier général, décor ou terrain (forêt, colline, rivière, ruines…). Donne le prompt Gemini dans l'angle et le style validés, puis extrait les sprites de l'image reçue.
---

# Style visuel du jeu

Ce skill fixe l'angle de vue et le style **validés par l'utilisateur** pour tout ce qui apparaît sur le champ de bataille et la carte : troupes, personnages sur le terrain, bâtiments, décors et terrains. Il ne couvre pas les portraits des personnages (cartes, fiches), dont le style reste à définir.

Les images sont générées par l'utilisateur avec **Gemini (Nano Banana)**. Le rôle de Claude : écrire le prompt, analyser l'image reçue, puis extraire les sprites avec le script fourni. Claude ne génère pas les images lui-même.

## Le style validé

Références dans `docs/style/references/` :
- `cavaliers_12_reference.png` : la planche de 12 cavaliers qui a été validée (angle et style de référence).
- `cavalier_seul_reference.png` : un cavalier extrait, à joindre comme modèle dans Gemini.
- `infanterie_armee_reference.jpg` : armée de 1 000 fantassins vue de haut (bon réalisme).
- `formation_test.png` : le rendu validé en formation, à la taille du jeu.
- `carte_champ_de_bataille_reference.webp` : la cible de style des cartes de bataille (jeu de stratégie moderne, réaliste mais lisible, Provence au printemps).

Règles :
- **Caméra haute et inclinée** (environ 55 à 70°), comme un général qui regarde la bataille du haut d'une colline. On voit le dessus des casques et des épaules, et le sujet de dos ou de trois quarts selon la direction.
- **Photoréaliste**, lumière naturelle de jour, matières mates, fer terne, couleurs naturelles et terreuses. Pas de peinture, pas d'illustration, pas de rendu 3D, pas de style dessin animé, pas de contour noir.
- **Fond vert pur uni (#00FF00)**, sans ombre, sans sol, sans texte, sans grille.
- **Taille en jeu** : un soldat fait environ 30 à 35 pixels de haut. Les détails fins (lances) disparaissent à cette taille : c'est accepté.
- **Pas de recoloration des troupes** : les joueurs se distinguent par leurs bannières.

## Méthode (leçons des essais précédents)

0. **Toujours demander l'accord de l'utilisateur avant toute génération payante** (Meshy, Gemini…), en annonçant le coût prévu. Une génération = un accord.

1. **Ne jamais demander d'animation image par image** à Gemini : il produit des fantômes flous et des incohérences. Les mouvements sont faits dans le code (glissement, balancement, poussière).
2. **Ne jamais demander une armée entière pour la découper** : les sujets se touchent et la découpe les coupe en deux. Demander des **sujets individuels séparés** sur une planche, puis le jeu les multiplie en formation.
3. **Une planche = 12 sujets, en grille de 4 colonnes × 3 rangées**, bien espacés, tous orientés vers le haut de l'image, tous à la même taille, avec des petites variations entre eux (variantes pour éviter l'effet clone).
4. **Joindre un sujet seul comme modèle** (par exemple `cavalier_seul_reference.png`), jamais l'image d'une armée entière : Gemini a déjà recopié une armée de référence en fond flou.
5. **Ouvrir une nouvelle conversation Gemini** à chaque nouveau type de sujet : il s'accroche sinon à l'image précédente.
6. **Récupérer l'image avec le bouton de téléchargement de Gemini**, pas par copier-coller ni capture d'écran (risque de mélange et de perte de résolution).
7. **Ne jamais redresser la perspective ni étirer une image** : ça rend flou. On ne fait que réduire.
8. La version gratuite de Gemini a une **limite d'images par jour** : viser un ou deux essais par sujet, avec un prompt complet du premier coup.

## Modèle de prompt (à adapter au sujet)

Joindre l'image de référence, puis :

```
The attached image is my style reference. Copy EXACTLY its camera angle, its photorealistic style, its lighting and its level of detail.

Draw 12 individual [SUJET], arranged in a grid of 4 columns and 3 rows, with LARGE empty green space between them: none of them touches or overlaps another, each one is fully separated by green background on all sides.

- Camera: high above and tilted, about 60 degrees, like a general watching from a hilltop. We see the top of the helmets and shoulders.
- Every [SUJET] faces the TOP of the image.
- All of them at the same size, each one complete and whole.
- Small natural variations between them: [VARIATIONS].
- Photorealistic, natural daylight, matte materials, dull iron, natural earthy colors. Not a painting, not an illustration, not a 3D render, no black outline, no glow, no blur.
- Plain flat pure green background (#00FF00) everywhere, no shadows, no ground, no text, no grid lines.
- Do not copy or include the reference image itself in the result.
```

Adaptations :
- **Soldats (infanterie, archers…)** : décrire l'équipement exact et l'interdire tout le reste (« no sword, no scabbard… »). Variations : couleurs de tenues, petits détails d'équipement.
- **Cavaliers** : variations de robes de chevaux (bai, alezan, noir, gris, isabelle). En formation, les cavaliers sont plus espacés que les fantassins, car les chevaux ont besoin de plus de place.
- **Personnage sur le terrain** (un général, un guerrier mystique) : 1 à 4 sujets au lieu de 12, reconnaissables à leur tenue, mais à la même échelle que les soldats.
- **Bâtiments** (tente de quartier général, palissade, tour…) : même caméra. On voit le toit et la façade tournée vers le bas de l'image. Un seul bâtiment par case de la grille.
- **Cartes de bataille** : ne jamais demander une carte entière en une image (Gemini ne sait pas dézoomer, et une seule image est trop petite pour des milliers de soldats). La carte est assemblée par le code à partir de pièces dans le style de `carte_champ_de_bataille_reference.webp` : textures de sol raccordables et planches d'éléments (arbres, bosquets, rochers, fermes, chapelle, tour en ruine, ponts, murets). Style : jeu de stratégie moderne, réaliste mais simplifié et lisible, contours nets, couleurs naturelles un peu vives. Pas de photo réelle.
- **Terrains** (herbe, forêt, colline, marais, ruines, eau) : même caméra, mais demander une **texture de sol vue de haut, raccordable sur ses quatre bords** (« seamless tileable texture »), sans fond vert, sans personnage. Pour les éléments posés (arbre isolé, rocher, ruine), utiliser la grille de 12 sur fond vert.

## Traitement de l'image reçue

Analyser d'abord l'image : angle, style, sujets entiers, séparés, fond vert propre, pas de fantôme. Dire honnêtement ce qui ne va pas avant de traiter.

Puis extraire avec :

```bash
python3 -I .claude/skills/style-visuel/scripts/extraire_sprites.py CHEMIN_IMAGE DOSSIER_SORTIE --prefixe cavalier --formation
```

Le script retire le fond vert, découpe chaque sujet sans le couper, et fabrique un aperçu de formation (serrée et lâche) à la taille du jeu. Montrer l'aperçu à l'utilisateur. Une seule passe, sans itérations inutiles : l'utilisateur surveille ses crédits.
