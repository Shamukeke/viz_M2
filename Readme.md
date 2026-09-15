# Cellule de recrutement

**Question métier.** Le directeur sportif cherche un ailier rapide et bon dribbleur, hors des
cinq grands championnats, avec une note globale (OVR) supérieure à 75. L'application filtre
17 700+ joueurs par championnat, poste et seuils (OVR, PAC, DRI), avec un raccourci pour exclure
directement Premier League / Liga / Bundesliga / Serie A / Ligue 1.

**Choix des graphiques.**

- *Distribution* (histogramme de l'OVR) : une seule variable quantitative, pour voir où se
  situe la sélection par rapport au seuil de 75 et si le pool de joueurs est suffisant.
- *Comparaison* (boxplot du dribble par poste) : croise une variable quantitative (DRI) et
  une catégorielle (poste), pour vérifier objectivement si les ailiers dribblent mieux que
  les autres postes, sur un axe partagé 0-100.
- *Relation* (nuage de points PAC × DRI) : deux variables quantitatives, pour repérer les
  profils à la fois rapides et techniques — exactement le croisement demandé par le recruteur.
- *Bonus* : radar PAC/SHO/PAS/DRI/PHY pour comparer deux joueurs présélectionnés en face-à-face.

**Limites du dataset.** Les notes (OVR, PAC, DRI...) sont des ratings de jeu vidéo (EA Sports FC),
pas des mesures de performance en match. Exemple concret : le dribble (DRI) des gardiens est
artificiellement élevé dans ce jeu de données (proche de celui des ailiers), ce qui fausserait
la comparaison par poste si on ne les excluait pas du boxplot. Autre piège : le dataset mélange
compétitions masculines et féminines dont les notes ne sont pas calibrées de la même façon — d'où
le filtre "Compétition" qui empêche de les comparer par erreur.

**Lexique des notes (0 à 99, aussi rappelé dans l'app).**

| Sigle | Signification |
|---|---|
| OVR | Note globale (Overall) |
| PAC | Vitesse (Pace) |
| SHO | Tir (Shooting) |
| PAS | Passe (Passing) |
| DRI | Dribble (Dribbling) |
| DEF | Défense (Defending) |
| PHY | Physique (Physicality) |

Postes : GK gardien, CB défenseur central, LB/RB latéral gauche/droit, CDM/CM/CAM milieu
défensif/central/offensif, LM/RM milieu gauche/droit, LW/RW ailier gauche/droit, ST attaquant.

Lancement : `streamlit run app.py`
