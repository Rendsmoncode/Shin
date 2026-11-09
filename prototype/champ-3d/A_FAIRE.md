# Prototype du champ de bataille : à faire

Retours de l'utilisateur (validé : le rendu des armées, le mode marche et les forêts lui plaisent beaucoup).

- [x] Varier la densité des forêts (bois clairsemés, forêts denses, bosquets isolés) pour des cartes plus diversifiées.
- [ ] Ajouter d'autres espèces d'arbres (pin parasol, olivier, cyprès, buissons de garrigue).
- [ ] Soldats vus de face et de profil (les armées doivent pouvoir se faire face et tourner).
- [x] Agrandir la carte à 3 km × 2 km.
- [x] Rendre le prototype jouable : sélectionner une armée, la déplacer, brouillard de guerre.
  - Fait : sélection (clic, Maj+clic, touches 1-2-3), ordre de marche au clic droit, vitesse selon le terrain (forêt, pente, gué, falaise infranchissable), brouillard avec lignes de vue (relief, arbres, colline +50 %, caché en forêt sauf à moins de 50 m), rouges en patrouille.
- [x] Le combat au contact (calcul de puissance, pertes, retrait des blocs).
  - Fait : manches de combat (3 s, deviendront des tours), puissance = hommes × valeur × terrain × charge ± hasard, pertes selon le rapport de force, écrasement seulement à l'arrivée d'une attaque très déséquilibrée, dispersion sous 10 hommes, repli en marchant dans l'autre sens, soldats retirés et bannière mise à jour, chiffres de pertes, victoire / défaite. Panneau « Réglages du combat » (valeurs modifiables, gardées dans le navigateur, copiables) avec simulateur de 1 000 combats. Les valeurs sont en haut du code (REGLAGES_DEFAUT).
- [x] Une mini-carte pour se repérer et s'y rendre en un clic.
  - Fait : coin bas droit, relief, rivière, forêts, brouillard, armées visibles (bloc orienté, or si choisie), trajets, cadre de la vue ; clic ou glisser pour y aller, clic droit pour y envoyer les armées choisies (ou marcher sur une armée rouge).
- [ ] Le mode tour par tour (5 actions par tour, chrono d'une minute).
- [ ] Remplacer le sol et les rochers provisoires par des textures et des modèles dans le style de référence.
- [x] Bannières des joueurs au-dessus des armées.
  - Fait : étendard planté au milieu de l'armée (hampe, drapeau à queue d'aronde à la couleur et à l'emblème du joueur : soleil pour les bleus, tour pour les rouges), plaque avec le nom du général et l'effectif réel, contour doré si choisie, taille lisible de près comme de loin. L'effectif se redessine tout seul quand il change (prêt pour le combat).
