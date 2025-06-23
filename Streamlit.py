"""""Creation de l'interface streamlit, 
Pour avoir un interaction plus dynamique avec l'utilisateur   """""

# streamlit : permet de créer des interfaces web interactives en Python
import streamlit as st

# streamlit_folium : permet d'intégrer des cartes Folium interactives dans une application Streamlit
from streamlit_folium import st_folium

# folium : utilisé pour créer des cartes interactives basées sur Leaflet.js
import folium

# requests : permet de faire des requêtes HTTP pour récupérer des données à partir d'API web
import requests

# datetime, timedelta : utilisés pour manipuler les dates et les heures (ex : calculer des intervalles de temps)
from datetime import datetime, timedelta

# pytz : permet de gérer les fuseaux horaires (utile pour convertir les heures locales ou UTC)
import pytz

# pandas : bibliothèque pour manipuler, analyser et structurer des données
import pandas as pd

# plotly.express : permet de créer facilement des graphiques interactifs (ex : courbes, cartes, etc.)
import plotly.express as px

# Fonction pour définir une image d'arrière-plan animée (GIF) dans l'application Streamlit
def set_background_image():
    # CSS intégré pour personnaliser l'apparence de l'application (stApp est la classe principale de Streamlit)
    page_bg_img = '''
    <style>
    .stApp {
        /* URL de l'image d'arrière-plan (ici un GIF depuis Giphy) */
        background-image: url("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzIxcWV6OHVhb25yNDB6NXBoY29uaGU3a2tnMWFvdDRxbXQ5Z2lsZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7qDKdHAqamtq0uBi/giphy.gif");

        /* L'image couvre toute la surface de l'écran */
        background-size: cover;

        /* Centre l'image sur la page */
        background-position: center;

        /* Empêche l'image de se répéter */
        background-repeat: no-repeat;
    }
    </style>
    '''
    # Injection du style CSS dans la page via Markdown, avec autorisation du HTML
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Convertir un angle (en degrés) en une direction cardinale (ex : Nord, Sud-Ouest, etc.)
def angle_to_direction(angle):
    # Liste des 8 directions cardinales principales (chaque direction couvre 45°)
    directions = ['Nord', 'Nord-Est', 'Est', 'Sud-Est', 'Sud', 'Sud-Ouest', 'Ouest', 'Nord-Ouest']

    # Calcul de l’index dans la liste en divisant l’angle en secteurs de 45°
    # On ajoute 22.5 pour centrer les plages de direction (ex : Nord = de 337.5° à 22.5°)
    idx = int((angle + 22.5) % 360 / 45)

    # Retourne la direction correspondante à l'angle
    return directions[idx]

# Interface

# Configure la page Streamlit : mise en page centrée, titre de l'onglet dans le navigateur
st.set_page_config(layout="centered", page_title="Météo Drone Delivery")

# Applique l'image d'arrière-plan définie par la fonction set_background_image()
set_background_image()

# Affiche un titre principal en haut de la page Streamlit
st.title("🌍 Sélectionnez un point de livraison sur la carte")

# Carte interactive

# Crée une carte Folium centrée sur Paris (coordonnées : 48.85°N, 2.35°E) avec un zoom initial de 4
m = folium.Map(location=[48.85, 2.35], zoom_start=4)

# Ajoute une fonctionnalité qui affiche les coordonnées latitude/longitude lorsqu'on clique sur la carte
folium.LatLngPopup().add_to(m)

# Affiche un petit texte informatif en bleu pour guider l'utilisateur
st.markdown('<p style="color:blue">Cliquez sur la carte pour sélectionner les coordonnées.</p>', unsafe_allow_html=True)

# Intègre la carte Folium dans l'application Streamlit et récupère les données de clic (coordonnées choisies)
map_data = st_folium(m, width=700, height=500)

# Si l'utilisateur clique sur la carte et que des coordonnées sont disponibles
if map_data and map_data["last_clicked"]:
    # Récupère la latitude et la longitude du point cliqué par l'utilisateur
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    # Affiche un message de confirmation avec les coordonnées sélectionnées (arrondies à 4 décimales)
    st.success(f"📍 Coordonnées sélectionnées : {lat:.4f}, {lon:.4f}")

    # 📡 Préparation de l'URL pour appeler l'API météo Open-Meteo
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=wind_speed_10m,wind_direction_10m,"
        f"wind_speed_80m,wind_direction_80m,"
        f"wind_speed_120m,wind_direction_120m,"
        f"wind_speed_180m,wind_direction_180m"
        f"&timezone=auto"
    )

    try:
        # Envoie une requête HTTP GET à l'API et transforme la réponse en dictionnaire JSON
        response = requests.get(url).json()

        # Récupère les heures disponibles dans les données météo
        heures_disponibles = response["hourly"]["time"]

        # Convertit les heures ISO en objets datetime (plus faciles à manipuler)
        heures_disponibles_dt = [datetime.fromisoformat(h) for h in heures_disponibles]

        # Interface pour sélectionner une date de livraison avec un calendrier interactif
        st.subheader("🗓️ Sélection de la date de livraison")

        # Définition des limites de sélection : entre aujourd’hui et dans 7 jours
        min_date = datetime.now().date()
        max_date = (datetime.now() + timedelta(days=7)).date()

        # Affiche un calendrier où l'utilisateur choisit la date de livraison
        date_selectionnee = st.date_input(
            "Choisissez la date de livraison",
            min_value=min_date,
            max_value=max_date,
            value=min_date
        )

        # Filtre les heures météo uniquement pour la date sélectionnée
        heures_du_jour = [h for h in heures_disponibles_dt if h.date() == date_selectionnee]

    # Vérifie qu’il y a bien des heures disponibles pour la date sélectionnée
    if heures_du_jour:
        # Affiche une liste déroulante pour choisir l'heure exacte de livraison
        heure_selectionnee = st.selectbox("Sélectionnez l'heure", heures_du_jour)

        # Trouve l’index de cette heure dans la liste complète des horaires météo
        index_horaire = heures_disponibles_dt.index(heure_selectionnee)

        # 📊 Préparation des données météo multi-altitudes
        altitudes = [10, 80, 120, 180]  # Altitudes standards (en mètres) pour les mesures de vent

        # Liste qui va contenir les données météo pour chaque altitude
        meteo_multi_alt = []

        # Boucle sur chaque altitude pour récupérer les données correspondantes
        for alt in altitudes:
            # Récupère la vitesse du vent à l’altitude donnée, pour l'heure sélectionnée
            vitesse = response["hourly"].get(f"wind_speed_{alt}m", [None])[index_horaire]

            # Récupère la direction du vent à cette altitude
            direction = response["hourly"].get(f"wind_direction_{alt}m", [None])[index_horaire]

            # Crée un dictionnaire avec les données météo pour cette altitude
            meteo_multi_alt.append({
                "Altitude (m)": alt,
                "Vitesse (m/s)": round(vitesse, 2) if vitesse else None,  # arrondi à 2 décimales
                "Direction (°)": round(direction) if direction else None,  # direction en degrés
                "Direction": angle_to_direction(direction) if direction else None,  # direction cardinale
                "Température (°C)": round(temperature_standard(alt) - 273.15, 2),  # conversion K → °C
                "Pression (kPa)": round(pression_standard(alt) / 10, 2)  # conversion hPa → kPa
            })

        # 🔽 Trie les données météo par altitude décroissante (du plus haut au plus bas)
        meteo_multi_alt.sort(key=lambda x: x['Altitude (m)'], reverse=True)

        # Convertit la liste de dictionnaires en un DataFrame Pandas pour un affichage structuré
        df_meteo = pd.DataFrame(meteo_multi_alt)

        # 📊 Affichage du tableau
        st.subheader("📊 Données météorologiques")

        # Affiche un tableau interactif avec des couleurs :
        # - dégradé bleu pour la vitesse du vent
        # - dégradé rouge pour la température
        st.dataframe(
            df_meteo.style
            .background_gradient(subset=["Vitesse (m/s)"], cmap="Blues")
            .background_gradient(subset=["Température (°C)"], cmap="Reds"),
            width=800
        )

        # 📈 Graphiques
        st.subheader("📈 Visualisations")

        # ➤ Graphique linéaire : Vitesse du vent selon l'altitude
        fig_vitesse = px.line(
            df_meteo,
            x="Altitude (m)",
            y="Vitesse (m/s)",
            title="Vitesse du vent par altitude",
            markers=True,  # Ajoute des marqueurs sur les points
            color_discrete_sequence=["#3498DB"]  # Couleur personnalisée (bleu)
        )

        # Affiche le graphique dans Streamlit
        st.plotly_chart(fig_vitesse, use_container_width=True)

        # ➤ Tendance du vent : représentation polaire de la direction et vitesse du vent
        if all(df_meteo["Direction (°)"].notna()):  # Vérifie que toutes les directions sont valides
            fig_rose = px.bar_polar(
                df_meteo,
                r="Vitesse (m/s)",  # Rayon = vitesse du vent
                theta="Direction (°)",  # Angle = direction du vent en degrés
                color="Altitude (m)",  # Couleur selon l'altitude
                title="Tendance du vent",
                template="plotly_dark",  # Thème sombre
                color_continuous_scale="Viridis"  # Échelle de couleur
            )
            # Affiche la tendance des vents
            st.plotly_chart(fig_rose, use_container_width=True)

            # 📍 Carte de localisation
            st.subheader("📍 Position final de livraison")

            # Crée une carte centrée sur les coordonnées sélectionnées, avec zoom plus rapproché
            m = folium.Map(location=[lat, lon], zoom_start=10)

            # Ajoute un marqueur sur la carte avec info sur la date/heure de livraison
            folium.Marker(
                [lat, lon],
                popup=f"Livraison: {date_selectionnee} {heure_selectionnee.strftime('%H:%M')}",
                icon=folium.Icon(color="green", icon="truck")
            ).add_to(m)

            # Affiche la carte avec le marqueur dans Streamlit
            st_folium(m, width=700, height=300)

            # Si aucune donnée météo disponible pour la date sélectionnée
            else:
            st.warning("Aucune donnée disponible pour cette date.")

            # Gestion des erreurs pendant la récupération des données API ou traitement
            except Exception as e:
            st.error("Erreur lors de la récupération des données météo.")
            st.exception(e)

            # Si l'utilisateur n’a pas encore cliqué sur la carte
            else:
            st.info("Veuillez sélectionner un point sur la carte pour commencer.")






















