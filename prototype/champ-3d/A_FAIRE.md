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
- [x] Le mode tour par tour (5 actions par tour, chrono d'une minute).
  - Fait : joueurs en même temps (ordres pendant le chrono, puis mouvement et combat de tout le monde), 1 ordre par armée et par tour, 5 au plus, marche longue qui continue gratuitement, cercle vert de la marche du tour, barre du tour (chrono, actions, Fin du tour / Entrée), 3 manches de combat par tour. Réglages modifiables (durée du tour, marche par tour, actions, manches). Bouton pour repasser en temps réel. Les actions comptent une armée = un homme clé, en attendant le ticket des hommes clés.
- [ ] Remplacer le sol et les rochers provisoires par des textures et des modèles dans le style de référence.
- [x] Bannières des joueurs au-dessus des armées.
  - Fait : étendard planté au milieu de l'armée (hampe, drapeau à queue d'aronde à la couleur et à l'emblème du joueur : soleil pour les bleus, tour pour les rouges), plaque avec le nom du général et l'effectif réel, contour doré si choisie, taille lisible de près comme de loin. L'effectif se redessine tout seul quand il change (prêt pour le combat).
- [x] Hommes clés, points et quartier général caché.
  - Fait : un QG par camp (tente à l'arrière, garde de 150 hommes, 3 gardes rapprochés, PV du général), invisible pour l'ennemi sauf soldats à moins de 250 m, vision 200 m, se déplace lentement (coûte une action). Points : général 3, chaque armée (sous-général) 1 ; une armée détruite fait perdre 1 point, le QG pris 3 ; défaite à 0 point. Actions par tour = hommes clés (armées + général), 5 au plus. Réglages du QG dans le panneau, option QG dans le simulateur.
- [x] Cartes de plusieurs tailles et petites batailles.
  - Fait : écran « Nouvelle bataille » (chefs, type, effectifs des deux armées, batailles toutes prêtes petite / moyenne / grande, contrôles : 10 à 5 000 hommes par unité, pas deux fois le même chef, 300 hommes minimum). Carte petite (1,05 × 0,7 km), moyenne (1,95 × 1,3 km) ou grande (3 × 2 km) selon la plus grande armée : réduction de la grande carte avec les mêmes pentes, forêts et rochers en proportion, placement de départ automatique (QG à l'arrière). 1 soldat affiché = 4 hommes à partir de 3 000 hommes. Vision et vitesses gardées en mètres réels.
- [x] Livret de règles (bouton dans le panneau) : rappel des règles de la bataille rangée avec les valeurs en cours, celles modifiées en doré.
- [x] Angle d'attaque : de face, de flanc (×1,3) ou de dos (×1,6) selon la position de l'attaquant par rapport à l'avant de sa cible ; annonce au début du combat ; l'armée attaquée se retourne face à son principal assaillant après 2 manches. Réglable, dans le simulateur et dans le livret.
- [x] Placement de départ en 59 secondes : cadre bleu (sa moitié de carte), clic droit pour placer les armées choisies, R pour les tourner, « Prêt » ou Entrée ; l'adversaire se place au hasard dans sa zone et reste caché pendant le placement. Durée réglable.
