"""
Ce module contient la classe `InterfaceStreamlit`, responsable de l'affichage
de l'interface interactive avec l'utilisateur via Streamlit.

  Elle permet de :
     - Sélectionner une position cible sur une carte (via folium),
     - Récupérer les données météo correspondantes via l'API Open-Meteo,
     - Afficher les profils de vent, température et pression par altitude,
     - Lancer la simulation de trajectoire (optimisation convexe),
     - Visualiser les résultats (graphes 2D, 3D et animation GIF).

Auteurs : Wilson David Parra Oliveros - Syrine Boudef - Linda Ghazouani

Date : 26/06/2026
"""

# Importations des bibliotheques necessaires
import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
from datetime import datetime, timedelta
import pytz
import pandas as pd
import plotly.express as px
from importer_vent import *
from simultion_final import *

class InterfaceStreamlit:
    """
    Classe principale pour gérer l'interface graphique avec Streamlit.

        Attributs :
            lat (float) : Latitude du point sélectionné par l'utilisateur.
            lon (float) : Longitude du point sélectionné.
            date_selectionnee (datetime.date) : Date de livraison choisie.
            heure_selectionnee (datetime.datetime) : Heure exacte sélectionnée.
            index_horaire (int) : Index de l'heure dans les données météo.
            response (dict) : Données météo brutes reçues depuis Open-Meteo.
    """
    def __init__(self):
        """
        Initialise les variables de l'interface : position, date, heure, données météo, etc.
        """
        self.lat = None
        self.lon = None
        self.date_selectionnee = None
        self.heure_selectionnee = None
        self.index_horaire = None
        self.response = None

    def temperature_standard(self, h):
        """
        Calcule la température standard (modèle ISA) à une altitude donnée.

          Paramètre :
            h (float) : Altitude en mètres.

          Retour :
            float : Température en Kelvin à l'altitude h.
        """
        T0 = 288.15
        lapse_rate = 0.0065
        return T0 - lapse_rate * h

    def pression_standard(self, h):
        """
        Calcule la pression atmosphérique standard ISA pour une altitude donnée.

        Paramètres :
        - h : altitude en mètres.

        Retour :
        - Pression en hPa.
        """
        T0 = 288.15
        P0 = 1013.25
        lapse_rate = 0.0065
        g = 9.80665
        M = 0.0289644
        R = 8.31447
        return P0 * (1 - (lapse_rate * h) / T0) ** ((g * M) / (R * lapse_rate))

    def angle_de_direction(self, angle):
        """
        Convertit un angle en degrés en une direction cardinale (ex: Nord, Sud-Ouest...).

        Paramètres :
        - angle : angle en degrés.

        Retour :
        - Nom de la direction (str).
        """
        directions = ['Nord', 'Nord-Est', 'Est', 'Sud-Est', 'Sud', 'Sud-Ouest', 'Ouest', 'Nord-Ouest']
        idx = int((angle + 22.5) % 360 / 45)
        return directions[idx]

    def set_background_image(self):
        """
        Applique un fond d’écran animé à l’application Streamlit à l’aide de CSS personnalisé.
        """
        page_bg_img = '''
        <style>
        .stApp {
            background-image: url("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzIxcWV6OHVhb25yNDB6NXBoY29uaGU3a2tnMWFvdDRxbXQ5Z2lsZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7qDKdHAqamtq0uBi/giphy.gif");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

    def afficher_interface(self):
        """
        Affiche l’interface utilisateur principale : carte de sélection, récupération météo,
        et bouton de lancement de simulation.
        """
        st.set_page_config(layout="centered", page_title="Météo Drone Delivery")
        # mettre la couleur d'ecriture en rouge
        st.markdown("""
        <style>
        /* Texte en rouge partout */
        html, body, [class*="st-"], .stApp {
            color: red !important;
        }

        /* Éléments spécifiques */
        h1, h2, h3, h4, h5, h6, p, div, span {
            color: red !important;
        }

        /* Forcer la couleur dans les tableaux */
        thead tr th, tbody tr td {
            color: red !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Eviter d'avoir un espace blan avec la map
        st.markdown("""
        <style>
        .element-container iframe {
            height: 500px !important;
            min-height: 500px !important;
            max-height: 500px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        self.set_background_image()
        st.title("🌍 Sélectionnez un point de livraison sur la carte")

        m = folium.Map(location=[48.85, 2.35], zoom_start=4)
        folium.LatLngPopup().add_to(m)
        st.markdown('<p style="color:blue">Cliquez sur la carte pour sélectionner les coordonnées.</p>', unsafe_allow_html=True)
        map_data = st_folium(m, width=700, height=500)

        if map_data and map_data["last_clicked"]:
            self.lat = map_data["last_clicked"]["lat"]
            self.lon = map_data["last_clicked"]["lng"]
            st.success(f"📍 Coordonnées sélectionnées : {self.lat:.4f}, {self.lon:.4f}")
            self.recuperer_donnees()

        if "clicked_point" not in st.session_state:
            st.session_state.clicked_point = None
        if map_data and map_data["last_clicked"] is not None:
            st.session_state.clicked_point = map_data["last_clicked"]
            st.success(f"📍 Point sélectionné : lat = {st.session_state.clicked_point['lat']:.4f}, "
                       f"lon = {st.session_state.clicked_point['lng']:.4f}")

        if st.session_state.clicked_point:
            if st.button("🚀 Lancer la simulation"):
                lat = st.session_state.clicked_point["lat"]
                lon = st.session_state.clicked_point["lng"]
                st.write(f" Simulation pour : lat = {lat:.4f}, lon = {lon:.4f}")

                with st.spinner("Simulation en cours..."):
                    simulateur = SimulerTrajectoire(lat=lat, lon=lon)
                    x_star, erreur, (xf, yf), z_t, time = simulateur.optimiser_trajectoire()
                    fig2d = simulateur.dessin_trajectoire_2D()
                    fig3d = simulateur.dessin_trajectoire_3D()
                    gif = simulateur.animation_trajectoire()

                st.image(gif, caption="🎮 Animation 3D de la trajectoire")
                st.image(fig2d, caption="📉 Trajectoire au sol (2D)")
                st.image(fig3d, caption="📊 Trajectoire complète (3D)")

    def recuperer_donnees(self):
        """
        Fait une requête HTTP vers l’API Open-Meteo pour récupérer les données de vent
        à différentes altitudes, pour la position et la date sélectionnées.
        """
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={self.lat}&longitude={self.lon}"
                f"&hourly=wind_speed_10m,wind_direction_10m,"
                f"wind_speed_80m,wind_direction_80m,"
                f"wind_speed_120m,wind_direction_120m,"
                f"wind_speed_180m,wind_direction_180m"
                f"&timezone=auto"
            )
            self.response = requests.get(url).json()

            heures_disponibles = self.response["hourly"]["time"]
            heures_disponibles_dt = [datetime.fromisoformat(h) for h in heures_disponibles]

            st.subheader("🗓️ Sélection de la date de livraison")
            min_date = datetime.now().date()
            max_date = (datetime.now() + timedelta(days=7)).date()
            self.date_selectionnee = st.date_input("Choisissez la date de livraison", min_value=min_date, max_value=max_date, value=min_date)
            heures_du_jour = [h for h in heures_disponibles_dt if h.date() == self.date_selectionnee]

            if heures_du_jour:
                self.heure_selectionnee = st.selectbox("Sélectionnez l'heure", heures_du_jour)
                self.index_horaire = heures_disponibles_dt.index(self.heure_selectionnee)
                self.afficher_meteo()
            else:
                st.warning("Aucune donnée disponible pour cette date.")

        except Exception as e:
            st.error("Erreur lors de la récupération des données météo.")
            st.exception(e)

    def afficher_meteo(self):
        """
        Affiche les données météo récupérées sous forme de tableau interactif et
        de visualisations (courbes et graphique polaire).
        """
        altitudes = [10, 80, 120, 180]
        meteo_multi_alt = []

        for alt in altitudes:
            vitesse = self.response["hourly"].get(f"wind_speed_{alt}m", [None])[self.index_horaire]
            direction = self.response["hourly"].get(f"wind_direction_{alt}m", [None])[self.index_horaire]

            meteo_multi_alt.append({
                "Altitude (m)": alt,
                "Vitesse (m/s)": round(vitesse, 2) if vitesse else None,
                "Direction (°)": round(direction) if direction else None,
                "Direction": self.angle_de_direction(direction) if direction else None,
                "Température (°C)": round(self.temperature_standard(alt) - 273.15, 2),
                "Pression (kPa)": round(self.pression_standard(alt) / 10, 2)
            })

        meteo_multi_alt.sort(key=lambda x: x['Altitude (m)'], reverse=True)
        df_meteo = pd.DataFrame(meteo_multi_alt)

        st.subheader("📊 Données météorologiques")
        st.dataframe(
            df_meteo.style
            .background_gradient(subset=["Vitesse (m/s)"], cmap="Blues")
            .background_gradient(subset=["Température (°C)"], cmap="Reds"),
            width=800
        )

        st.subheader("📈 Visualisations")
        fig_vitesse = px.line(df_meteo, x="Altitude (m)", y="Vitesse (m/s)", title="Vitesse du vent par altitude", markers=True)
        st.plotly_chart(fig_vitesse, use_container_width=True)

        if all(df_meteo["Direction (°)"].notna()):
            fig_rose = px.bar_polar(df_meteo, r="Vitesse (m/s)", theta="Direction (°)", color="Altitude (m)",
                                     title="Tendance du vent", template="plotly_dark")
            st.plotly_chart(fig_rose, use_container_width=True)

        st.subheader("📍 Position final de livraison")
        m = folium.Map(location=[self.lat, self.lon], zoom_start=10)
        folium.Marker([self.lat, self.lon], popup=f"Livraison: {self.date_selectionnee} {self.heure_selectionnee.strftime('%H:%M')}",
                      icon=folium.Icon(color="green", icon="truck")).add_to(m)
        st_folium(m, width=700, height=300)


if __name__ == "__main__":
    app = InterfaceStreamlit()
    app.afficher_interface()
