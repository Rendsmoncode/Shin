# Consignes pour Claude (projet Shin)

- **Lire d'abord `docs/VUE_D_ENSEMBLE.md`** : il explique la différence entre le jeu (monde persistant sur la carte d'Aubagne) et la bataille rangée en 3D (le prototype). Ne pas les confondre. Le mode raid façon Clash of Clans a été supprimé.

- **Toujours demander l'accord de l'utilisateur avant toute génération payante** (Meshy, Gemini, ou tout autre service qui consomme des crédits), en annonçant le coût prévu. Ne jamais enchaîner plusieurs générations payantes sans accord explicite pour chacune.
- L'utilisateur surveille ses crédits Claude : éviter les itérations inutiles, faire une seule passe quand c'est possible, et prévenir avant un travail coûteux.
- Répondre en français, simplement : l'utilisateur n'est pas développeur.
- **Équilibrage** : Claude peut modifier ou supprimer les éléments de règles qu'il a lui-même proposés s'ils bloquent un élément important ou déséquilibrent le jeu (accord d'Ayoub, voir le début de `docs/REGLES.md`), en informant toujours l'utilisateur de ce qui a changé et pourquoi.
- Les règles du jeu sont dans `docs/REGLES.md`, les personnages dans `docs/PERSONNAGES.md`, le style visuel dans le skill `style-visuel`.
- **Ne pas tester le jeu dans la session** (pas de rendu dans un navigateur headless, pas de captures d'écran) sauf si l'utilisateur le demande : coder, envoyer sur `main`, et l'utilisateur teste sur le site publié (`https://rendsmoncode.github.io/Shin/` : page de garde, le jeu dans `jeu/` (onglet Monde = carte de la ville `carte/`), test des batailles dans `champ-3d/`, tâches dans `taches/`).

- **Deux personnes travaillent sur le projet, chacune avec son Claude : Ayoub (le créateur du jeu) et Mathieu.** Avant de commencer : récupérer la dernière version de `main`.
- **Liste des tâches : `prototype/taches/taches.json`** (affichée sur le site dans `taches/`). La tenir à jour à chaque fois :
  - au début d'une session, la lire. Si la tâche demandée est « En cours » chez l'autre personne, le dire avant de toucher à quoi que ce soit ;
  - en commençant une tâche : statut « En cours » et responsable (Ayoub ou Mathieu), puis envoyer ce changement sur `main` tout de suite, avant de coder ;
  - en terminant : statut « Fait, à vérifier », dans le même envoi que le travail. « Fait » seulement quand l'utilisateur a validé sur le site ;
  - ajouter, modifier ou supprimer des tâches quand l'utilisateur le demande ou quand une décision change le plan (statut « Abandonné » plutôt que supprimer une tâche commencée). Une nouvelle tâche prend le plus grand `id` + 1, avec une phase déjà existante. Mettre à jour `maj` (date du jour) ;
  - garder le fichier valide (une tâche par ligne) : le vérifier avec `python3 -m json.tool` avant d'envoyer.
