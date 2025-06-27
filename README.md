# Simulateur de Trajectoire de Parachute Guidé

##  Description du projet
Ce projet Python propose une simulation interactive de la trajectoire d’un parachute guidé vers une cible donnée, en tenant compte des conditions météorologiques réelles (vents à différentes altitudes).

L’interface Streamlit permet à l’utilisateur de :
- sélectionner un point de livraison sur une carte,
- consulter les conditions météo du lieu (vitesse et direction du vent, pression, température),
- lancer une simulation d’atterrissage optimisé,
- visualiser les résultats sous forme de graphiques 2D, 3D et animation.

Le programme met en œuvre une optimisation convexe pour gérer dynamiquement la trajectoire.

---

##  Fonctionnalités principales
- Interface Web avec Streamlit et carte Folium
- Simulation de trajectoire via CVXPY (optimisation convexe)
- Récupération automatique des vents via l’API [Open-Meteo](https://open-meteo.com/)
- Visualisation des résultats :
  - Données météo tabulées et colorées
  - Graphe 2D de la trajectoire au sol
  - Graphique 3D et animation GIF

---

##  Structure du projet (POO)

Le projet est organisé en trois classes principales :

| Fichier               | Classe               | Rôle                                                                 |
|-----------------------|----------------------|----------------------------------------------------------------------|
| `simultion_final.py` | `SimulerTrajectoire` | Résolution convexe de la trajectoire guidée + visualisation         |
| `importer_vent.py`   | `ImportVent`         | Récupération et interpolation des vents à partir de l’API           |
| `interface.py`       | `InterfaceStreamlit` | Interface graphique, carte interactive, récupération météo, simulation |

---

##  Installation

```bash
# Cloner le répertoire
git clone https://github.com/votre_utilisateur/simulateur-parachute.git
cd simulateur-parachute

# Créer un environnement virtuel (optionnel mais recommandé)
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows

# Installer les dépendances
pip install -r requirements.txt
```
##  Utilisation

Lancer le fichier principal `main.py` avec la commande suivante :

```bash
streamlit run main.py
```

Vous pourrez alors :

* sélectionner un point sur la carte,
* choisir la date et l’heure de livraison,
* lancer la simulation et visualiser les résultats.

> **Remarque** : les fichiers de sortie (images/graphes) sont automatiquement enregistrés dans le répertoire de travail courant.

---

##  Exemple de sortie

* `graph2D_lat_lon.png` : image 2D de la trajectoire projetée au sol
* `graph3D_lat_lon.png` : image 3D avec l’altitude
* `trajectoire_lat_lon.gif` : animation dynamique de la descente

---

##  Auteur

**Wilson David Parra Oliveros**
**Syrine Boudef**
**Linda Ghazouani**

École de technologie supérieure (ÉTS), 2025
Projet réalisé dans le cadre du cours **Programmation Python-MGA802**

---

##  Licence

Projet académique — utilisation libre dans un contexte éducatif.
**Toute redistribution commerciale ou publication externe est interdite sans autorisation.**
