# Fiches des personnages

**Les fiches sont maintenant dans le jeu** : onglet **Fiches** (`https://rendsmoncode.github.io/Shin/jeu/#fiches`, ou directement `fiches/`).

- **Fichier de référence** : `prototype/fiches/fiches.json`. C'est lui que Claude met à jour.
- **Modifier une fiche** : sur le site, bouton « Modifier ». Les modifications sont gardées dans le navigateur ; le bouton « Exporter mes modifications » les copie (et télécharge un fichier) pour les envoyer à Claude, qui les intègre dans `fiches.json`. Une fois intégrées, « Effacer mes modifications ».
- Règles des stats et des effets : `REGLES.md` (sections 6 bis et 7) et `PERSONNAGES.md` (« La fiche d'un personnage »).
- Tous les chiffres sont indicatifs : ils seront réglés par simulation.


---

## Évolutions de Shin, Koby et Guts (SECRET : ne rien en mettre dans le jeu)

Dans le jeu, chacun n'a que sa **fiche de base** (commun), sans aucun indice qu'il évolue. Chaque évolution est une **nouvelle fiche** qui se débloque plus tard (seuils d'XP et de soldats ; l'**objet du mentor** débloque soit la fiche épique, soit la légendaire, ❓ à choisir). Chaque fiche reprend ce qui précède et ajoute ce qui suit (piste de travail, chiffres indicatifs).

### Shin

| Fiche | Ce qu'elle ajoute | Stats |
|---|---|---|
| Commun | Leader : Ses hommes ATK +5 %. ; Passif « Gamin des rues » : Quand il se bat en personne, ATK +15 %. | ATK 290 · DEF 230 · END 270 · INT 160 · VIT 250 · Aura 280 |
| Rare | Effet « La charge de Shin » (Jauge d'Aura) : L'unité qu'il mène ATK +40 % pendant 1 tour, et elle peut charger même en montée. | ATK 430 · DEF 350 · END 400 · INT 250 · VIT 370 · Aura 430 |
| Épique | Leader : Ses hommes ATK +15 %. ; Passif « L'instinct » : Révèle les embuscades à moins de 150 m de lui. ; Formation : Coin | ATK 620 · DEF 510 · END 580 · INT 360 · VIT 530 · Aura 620 |
| Légendaire | Leader : Ses hommes ATK et DEF +20 %. ; Stratégie : Marteau et enclume | ATK 820 · DEF 660 · END 760 · INT 470 · VIT 700 · Aura 810 |
| Sous les Cieux | Leader : Ses hommes ATK et DEF +30 %. ; Passif « Le plus grand général sous les cieux » : Sa jauge d'Aura se remplit 50 % plus vite, et ses hommes ATK +10 % tant qu'il est au front. ; Coup de grâce « Le saut du guandao » (Jauge d'Aura) : Achève une armée ennemie affaiblie. | ATK 960 · DEF 780 · END 900 · INT 550 · VIT 820 · Aura 950 |

### Koby

| Fiche | Ce qu'elle ajoute | Stats |
|---|---|---|
| Commun | Leader : Ses hommes DEF +5 %. ; Passif « Haki de l'observation » : Vision +30 %, et il voit les armées cachées à moins de 100 m. | ATK 250 · DEF 280 · END 280 · INT 210 · VIT 260 · Aura 270 |
| Rare | Effet « Soru » (Jauge d'Aura) : L'armée qu'il mène se déplace deux fois pendant 1 tour. | ATK 370 · DEF 430 · END 410 · INT 320 · VIT 400 · Aura 400 |
| Épique | Leader : Ses hommes DEF +15 %. ; Passif « Justice » : Contre un tyran (armée du jeu), ATK +20 %. ; Formation : Mur de boucliers | ATK 530 · DEF 620 · END 600 · INT 460 · VIT 570 · Aura 580 |
| Légendaire | Leader : Ses hommes ATK et DEF +20 %. ; Stratégie : Ville vide | ATK 700 · DEF 810 · END 780 · INT 600 · VIT 750 · Aura 760 |
| Sous les Cieux | Leader : Ses hommes ATK et DEF +30 %. ; Passif « Le héros de Rocky Port » : Les armées alliées à moins de 200 m de lui perdent 15 % d'hommes en moins. ; Coup de grâce « Le poing de la justice » (Jauge d'Aura) : Achève une armée ennemie affaiblie. | ATK 820 · DEF 950 · END 920 · INT 700 · VIT 880 · Aura 900 |

### Guts

| Fiche | Ce qu'elle ajoute | Stats |
|---|---|---|
| Commun (enfant) | Leader : Ses hommes ATK +5 %. ; Passif « Seul contre tous » : Quand il se bat en personne contre plus nombreux que lui, ATK +20 %. | ATK 280 · DEF 220 · END 300 · INT 120 · VIT 250 · Aura 200 |
| Rare | Effet « Le canon du bras » (Jauge d'Aura) : Un tir à distance qui fait de grosses pertes dans une armée ennemie. | ATK 420 · DEF 330 · END 450 · INT 180 · VIT 380 · Aura 300 |
| Épique | Passif « Le Dragon Slayer » : Ses coups ignorent 30 % de la DEF ennemie. ; Formation : Coin | ATK 600 · DEF 460 · END 630 · INT 250 · VIT 520 · Aura 420 |
| Légendaire | Leader : Ses hommes ATK +20 %. ; Stratégie : Attaque de nuit (renforcée) | ATK 820 · DEF 640 · END 850 · INT 330 · VIT 700 · Aura 580 |
| Guerrier mystique (trait Général) | Leader : Ses hommes ATK +30 %. ; Passif « Cent hommes » : Il peut tenir seul contre une armée entière. ; Attaque spéciale « Furie du Guerrier noir » (Jauge d'Aura) : Attaque très puissante (à définir). | ATK 2600 · DEF 2000 · END 2800 · INT 450 · VIT 900 · Aura 1000 |

### Les objets des mentors

Reçus au déblocage du 500 contre 500. Un objet **débloque une fiche** (l'épique ou la légendaire, ❓) et donne seulement un **léger bonus** : il ne doit pas être trop fort, puisqu'il sert déjà à débloquer la fiche.

| Objet | Pour | Léger bonus (piste) |
|---|---|---|
| Le guandao d'Ouki | Shin | quand il se bat en personne, ATK +10 % |
| Le Haki de l'armement | Koby | quand il se bat en personne, DEF +10 % |
| L'armure du Berserker | Guts | quand ses points de vie passent sous 50 %, ATK +15 % |
