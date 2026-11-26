# Bâtiments constructibles et leurs niveaux (proposition de Claude, 26/11, à valider par Ayoub)

> Tâche 25. Tout est 💡 (proposé) tant qu'Ayoub n'a pas validé. Les chiffres sont indicatifs : ils seront réglés à l'équilibrage (tâche 195).
> Rappel des règles (`REGLES.md`, section 3) : on **améliore les vrais lieux** de la ville, on **construit sur les espaces vides**, la maison du joueur est l'**hôtel de ville**, et on ne construit jamais un lieu majeur (seulement sa version modeste).

## 1. Les règles communes

- 💡 **Niveaux 1 à 10** pour chaque bâtiment, comme dans Rise of Kingdoms (version courte : 10 niveaux au lieu de 25).
- 💡 **Un bâtiment ne dépasse jamais le niveau de l'hôtel de ville.**
- 💡 **Coût** du niveau n = coût du niveau 1 × 1,6^(n−1). Du niveau 1 au niveau 10, le coût est multiplié par environ 70.
- 💡 **Durée** du niveau n = durée du niveau 1 × 1,7^(n−1), plafonnée à 3 jours. Les premiers niveaux prennent quelques minutes, pour que le début aille vite (tâche 115).
- 💡 **Deux files de construction** au départ, une troisième au niveau 6 de l'hôtel de ville. Les accélérateurs (boutique, coffres, récompenses de connexion) raccourcissent une construction.
- 💡 **Un vrai lieu amélioré** garde son nom réel sur la carte (« Boulangerie Dupont, niveau 4 »). Un bâtiment construit sur un espace vide porte un nom choisi par le joueur.
- 💡 **Pillage** : un bâtiment n'est jamais détruit. Un ennemi qui prend le quartier le récupère au même niveau.

## 2. L'hôtel de ville (la maison du joueur)

| Niveau | Ce qu'il débloque |
|---|---|
| 1 | Caserne, ferme, atelier, entrepôt ; 1 armée |
| 2 | Infirmerie, marché ; recrutement jusqu'à 200 hommes |
| 3 | Tour de guet, relais de messagers ; 2 armées |
| 4 | Académie, écurie ; recrutement jusqu'à 500 hommes (bataille rangée) |
| 5 | Garnison, stand de tir ; contrats de diplomatie |
| 6 | Forge, repaire d'espions ; 3e file de construction ; 3 armées |
| 7 | Atelier d'ingénieurs (pièges et constructions de bataille) |
| 8 | Ambassade (renforts envoyés aux alliés) ; 4 armées |
| 9 | Chambre forte |
| 10 | Bonus de capitale : toutes les productions +10 % ; 5 armées |

Coût du niveau 1 : 500 matériaux, 300 argent. Durée : 5 minutes.

## 3. Les vrais lieux à améliorer

Leur rôle vient de la table de `REGLES.md` (section 3). Chaque niveau augmente leur effet.

| Lieu réel | Effet par niveau | Effet spécial au niveau 10 |
|---|---|---|
| Maisons et immeubles | Population +8 % | Recrutement 20 % plus rapide dans le quartier |
| Commerces, restaurants, bars | Argent +10 % | Le commerce le plus haut du quartier attire des clients d'un quartier voisin (+5 % d'argent pour tout le quartier) |
| Champs, jardins, espaces verts | Nourriture +10 % | Les armées qui campent à côté ne consomment pas de vivres |
| Supermarchés, marchés | Nourriture +6 % et argent +6 % | Cours d'achat de la nourriture −10 % pour le propriétaire |
| Bricolage, BTP, carrières | Matériaux +10 % | Constructions du quartier −10 % de matériaux |
| Banques | Stockage d'argent protégé +10 % | La moitié de l'argent du quartier est protégée du pillage |
| Entrepôts, zones industrielles | Stockage de nourriture et de matériaux +10 % | Un quart du stock est protégé du pillage |
| Stades, gymnases | Entraînement des troupes 8 % plus rapide | Une amélioration de troupe gratuite par jour |
| Hôpitaux, cliniques, pharmacies | Soins 8 % plus rapides | Les tombés reviennent en 2 h au lieu de 3 h |
| Écoles, collèges, lycées | XP des généraux +5 % | Un livre d'XP par jour |
| Gendarmerie, police, pompiers | Défense du quartier +6 % | Une garnison de 100 hommes apparaît gratuitement en cas d'attaque |
| Gare, entrées d'autoroute | Déplacements depuis le quartier +5 % | Commerce avec les autres villes sans frais |
| Mairie, monuments, églises, musées | Lieux uniques ou majeurs : leur bonus vient de leur quête (`QUETES.md`) | — |

## 4. Les bâtiments à construire sur un espace vide

| Bâtiment | Effet | Effet par niveau | Version modeste de |
|---|---|---|---|
| **Caserne** | Recrute l'infanterie, puis les autres troupes selon son niveau (archers au 2, cavalerie au 4, troupes d'élite au 7) | Recrutement +8 % | Légion étrangère |
| **Ferme** (potager) | Nourriture | +8 % (moins qu'un vrai champ) | — |
| **Atelier** | Matériaux | +8 % | — |
| **Entrepôt** | Stockage de nourriture et de matériaux | +10 % | Zone industrielle |
| **Infirmerie** | Soigne les blessés | Soins +6 % | Hôpital |
| **Marché** | Échange de ressources avec les autres joueurs | Frais de vente −2 % | — |
| **Tour de guet** | Vision de la carte autour du quartier | Portée +10 % ; au 5, repère les espions ennemis | — |
| **Relais de messagers** | Messagers plus rapides (voir `REGLES.md`, section 11) | Vitesse des messagers +5 % ; au 8, les messages interceptés sont signalés | Gare |
| **Académie** | XP et recherches des généraux | XP +4 % | Lycée |
| **Écurie** | Vitesse de la cavalerie et des armées en marche | +3 % | — |
| **Garnison** | Défense du quartier (soldats qui restent sur place) | +100 hommes de garde par niveau | Gendarmerie |
| **Stand de tir** | Améliore les archers | ATK au tir +3 % | — |
| **Forge** | Améliore l'équipement de toutes les troupes | ATK ou DEF +2 % (au choix à chaque niveau) | — |
| **Repaire d'espions** | Missions d'espionnage, désinformation | Réussite des espions +4 % | — |
| **Atelier d'ingénieurs** | Pièges et constructions sur le champ de bataille (tâche 53) | Un type de piège ou de construction de plus tous les 2 niveaux | — |
| **Ambassade** | Envoie des renforts dans le quartier d'un allié | +200 hommes de renfort possibles par niveau | — |
| **Chambre forte** | Protège les ressources du pillage | +5 % de chaque ressource protégée | Banque |
| **Tour de défense** | Tire sur les armées qui attaquent le quartier | Dégâts +10 % | — |

- 💡 **Combien de bâtiments** : on peut construire autant de bâtiments qu'il y a d'espaces vides dans ses quartiers (tâche 81), mais **un seul de chaque type par quartier**, sauf la ferme, l'atelier et la tour de défense.

## 5. Questions pour Ayoub

- ❓ Dix niveaux, c'est assez ? (Rise of Kingdoms en a 25, ce qui fait durer le jeu des mois.)
- ❓ Un bâtiment pris par l'ennemi garde-t-il son niveau, ou perd-il quelques niveaux ?
- ❓ La tour de défense est-elle utile, sachant que la défense passe déjà par la garnison et les soldats ?
