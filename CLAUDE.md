# Consignes pour Claude (projet Shin)

- **Lire d'abord `docs/VUE_D_ENSEMBLE.md`** : il explique la différence entre le jeu (monde persistant sur la carte d'Aubagne), les raids façon Clash of Clans et la bataille rangée en 3D (le prototype). Ne pas les confondre.

- **Toujours demander l'accord de l'utilisateur avant toute génération payante** (Meshy, Gemini, ou tout autre service qui consomme des crédits), en annonçant le coût prévu. Ne jamais enchaîner plusieurs générations payantes sans accord explicite pour chacune.
- L'utilisateur surveille ses crédits Claude : éviter les itérations inutiles, faire une seule passe quand c'est possible, et prévenir avant un travail coûteux.
- Répondre en français, simplement : l'utilisateur n'est pas développeur.
- Les règles du jeu sont dans `docs/REGLES.md`, les personnages dans `docs/PERSONNAGES.md`, le style visuel dans le skill `style-visuel`.
- **Ne pas tester le jeu dans la session** (pas de rendu dans un navigateur headless, pas de captures d'écran) sauf si l'utilisateur le demande : coder, envoyer sur `main`, et l'utilisateur teste sur le site publié (`https://rendsmoncode.github.io/Shin/champ-3d/`).
