# Vue d'ensemble du jeu (à lire en premier)

Ce document explique comment les parties du jeu s'emboîtent. Le détail des règles est dans `REGLES.md`.

**Attention à ne pas confondre le jeu et la bataille.** Le jeu est un monde persistant de stratégie sur la carte d'Aubagne. La bataille rangée en 3D n'en est qu'**un des modes de combat**.

## Les trois niveaux du jeu

### 1. Le monde : la carte d'Aubagne (le jeu « principal », façon Crusader Kings III)
- Un **monde persistant en temps réel**, qui ne s'arrête jamais, sur la **vraie carte d'Aubagne et de La Valentine** (données OpenStreetMap, pas encore intégrées).
- Chaque joueur (le créateur du jeu, Nicolas, Mathieu) commence dans **son vrai quartier**, avec sa vraie maison comme hôtel de ville.
- On **s'agrandit** en prenant les quartiers neutres, puis ceux des autres joueurs.
- On y gère : l'**économie** (argent, nourriture, matériaux, population), les **généraux et personnages** (gacha), la **diplomatie** (contrats, alliances, trahison), et les **guerres** (long terme).
- Les **armées se déplacent sur les routes** de la carte d'Aubagne.
- Vue : carte zoomable comme CK3 (villes → quartiers → détails).

### 2. Le quartier et les raids (façon Clash of Clans / Rise of Kingdoms)
- Chaque quartier se **construit et s'améliore** (bâtiments réels transformés, constructions sur les espaces vides, défenses, pièges).
- Un **raid** est une attaque courte (3 minutes) sur un quartier : l'attaquant déploie ses troupes, qui agissent seules, contre les défenses. On gagne du **butin** (pillage) et des étoiles.
- C'est le mode utilisé quand **le défenseur n'est pas connecté** (ses défenses jouent seules).

### 3. La bataille rangée (tour par tour, façon Warhammer / Total War)
- Un **affrontement entre joueurs connectés**, sur un **champ de bataille séparé**, tiré au hasard (pas sur la carte d'Aubagne).
- Tour par tour : général dans son quartier général caché, sous-généraux, unités, 5 actions maximum par tour, brouillard de guerre, formations, terrain et relief.
- Jouable **dès 300 hommes**, sur une carte plus petite pour les petites armées (en dessous de 300, les combats se règlent automatiquement).
- Le vainqueur remporte la **mise ou l'objectif** (pas de pillage), tout le monde gagne de l'XP.
- **C'est ce que montre le prototype `prototype/champ-3d/`** : uniquement ce mode de combat, pas le jeu entier.

### Comment ils se relient
- Une **guerre** (niveau 1) se joue sur la carte d'Aubagne et se compose de plusieurs combats.
- Quand deux armées ou un joueur et un quartier s'affrontent : si les deux joueurs sont connectés → **bataille rangée** (niveau 3) ; sinon → **raid** façon Clash of Clans (niveau 2).

## Où en est le développement
- **Fait** : les règles de la bataille rangée et du raid, les personnages, le style visuel, et le **prototype 3D du champ de bataille** (`prototype/champ-3d/`).
- **Prochaine étape du prototype** : le rendre jouable (sélectionner une armée, la déplacer, brouillard de guerre). Voir `prototype/champ-3d/A_FAIRE.md`.
- **Plus tard** : la carte d'Aubagne (OpenStreetMap), le quartier et ses défenses, le gacha, puis les guerres (gardées pour la fin).
