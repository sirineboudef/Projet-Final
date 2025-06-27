"""
Ce module contient la classe `InterfaceStreamlit`, responsable de l'affichage
via Streamlit d'une interface utilisateur pour la sélection de position, récupération
météo, simulation de trajectoire, et visualisation.

Fonctionnalités :
- Sélection d'une position sur carte interactive (folium),
- Récupération météo (Open-Meteo API),
- Affichage des profils vent/température/pression,
- Simulation de trajectoire optimisée,
- Visualisation en 2D, 3D et GIF.

Auteurs : Wilson David Parra Oliveros, Syrine Boudef, Linda Ghazouani
Date : 26/06/2026
"""

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
    Interface utilisateur pour le simulateur de livraison guidée par drone.

    Permet la sélection d'une position sur carte, la récupération météo,
    la simulation de trajectoire et l'affichage des résultats.
    """
    def __init__(self):
        """Initialise les attributs nécessaires à l'interface."""
        self.lat = None
        self.lon = None
        self.date_selectionnee = None
        self.heure_selectionnee = None
        self.index_horaire = None
        self.response = None

    def temperature_standard(self, h):
        """
        Calcule la température standard ISA à l'altitude `h`.

        :param h: Altitude (m)
        :return: Température (K)
        """
        T0 = 288.15
        lapse_rate = 0.0065
        return T0 - lapse_rate * h

    def pression_standard(self, h):
        """
        Calcule la pression standard ISA à l'altitude `h`.

        :param h: Altitude (m)
        :return: Pression (hPa)
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
        Convertit un angle en direction cardinale.

        :param angle: Angle (degrés)
        :return: Direction cardinale (str)
        """
        directions = ['Nord', 'Nord-Est', 'Est', 'Sud-Est', 'Sud', 'Sud-Ouest', 'Ouest', 'Nord-Ouest']
        idx = int((angle + 22.5) % 360 / 45)
        return directions[idx]

    def set_background_image(self):
        """Applique un fond d'écran animé avec CSS dans Streamlit."""
        page_bg_img = '''<style>.stApp {
        background-image: url("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjEx.../giphy.gif");
        background-size: cover; background-position: center; background-repeat: no-repeat;}</style>'''
        st.markdown(page_bg_img, unsafe_allow_html=True)

    def afficher_interface(self):
        """
        Affiche l'interface Streamlit principale : carte,
        sélection date/heure, lancement de simulation.
        """
        st.set_page_config(layout="centered", page_title="Météo Drone Delivery")
        st.markdown("""<style>html, body, [class*='st-'], .stApp {color: red !important;}</style>""", unsafe_allow_html=True)
        st.markdown("""<style>.element-container iframe {height: 500px !important;}</style>""", unsafe_allow_html=True)

        self.set_background_image()
        st.title("🌍 Sélectionnez un point de livraison sur la carte")

        m = folium.Map(location=[48.85, 2.35], zoom_start=4)
        folium.LatLngPopup().add_to(m)
        st.markdown('<p style="color:blue">Cliquez sur la carte...</p>', unsafe_allow_html=True)
        map_data = st_folium(m, width=700, height=500)

        if map_data and map_data["last_clicked"]:
            self.lat = map_data["last_clicked"]["lat"]
            self.lon = map_data["last_clicked"]["lng"]
            st.success(f"📍 Coordonnées : {self.lat:.4f}, {self.lon:.4f}")
            self.recuperer_donnees()

        if "clicked_point" not in st.session_state:
            st.session_state.clicked_point = None

        if map_data and map_data["last_clicked"] is not None:
            st.session_state.clicked_point = map_data["last_clicked"]

        if st.session_state.clicked_point:
            if st.button("🚀 Lancer la simulation"):
                lat = st.session_state.clicked_point["lat"]
                lon = st.session_state.clicked_point["lng"]
                st.write(f"Simulation pour : lat = {lat:.4f}, lon = {lon:.4f}")

                with st.spinner("Simulation en cours..."):
                    simulateur = SimulerTrajectoire(lat=lat, lon=lon)
                    x_star, erreur, (xf, yf), z_t, time = simulateur.optimiser_trajectoire()
                    fig2d = simulateur.dessin_trajectoire_2D()
                    fig3d = simulateur.dessin_trajectoire_3D()
                    gif = simulateur.animation_trajectoire()

                st.image(gif, caption="🎮 Animation 3D")
                st.image(fig2d, caption="📉 Trajectoire au sol (2D)")
                st.image(fig3d, caption="📊 Trajectoire complète (3D)")

    def recuperer_donnees(self):
        """
        Récupère les données météo pour les coordonnées choisies via l'API Open-Meteo,
        puis permet à l'utilisateur de choisir une date/heure de livraison.
        """
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}"
                f"&hourly=wind_speed_10m,wind_direction_10m,wind_speed_80m,wind_direction_80m,"
                f"wind_speed_120m,wind_direction_120m,wind_speed_180m,wind_direction_180m&timezone=auto"
            )
            self.response = requests.get(url).json()
            heures_disponibles = self.response["hourly"]["time"]
            heures_dt = [datetime.fromisoformat(h) for h in heures_disponibles]

            st.subheader("🗓️ Date de livraison")
            min_date = datetime.now().date()
            max_date = (datetime.now() + timedelta(days=7)).date()
            self.date_selectionnee = st.date_input("Choisissez la date", min_value=min_date, max_value=max_date, value=min_date)

            heures_jour = [h for h in heures_dt if h.date() == self.date_selectionnee]
            if heures_jour:
                self.heure_selectionnee = st.selectbox("Sélectionnez l'heure", heures_jour)
                self.index_horaire = heures_dt.index(self.heure_selectionnee)
                self.afficher_meteo()
            else:
                st.warning("Aucune donnée disponible pour cette date.")
        except Exception as e:
            st.error("Erreur lors de la récupération des données.")
            st.exception(e)

    def afficher_meteo(self):
        """
        Affiche les données météo sous forme de tableau et de graphiques interactifs.
        """
        altitudes = [10, 80, 120, 180]
        meteo_multi_alt = []
        for alt in altitudes:
            vitesse = self.response["hourly"].get(f"wind_speed_{alt}m")[self.index_horaire]
            direction = self.response["hourly"].get(f"wind_direction_{alt}m")[self.index_horaire]
            meteo_multi_alt.append({
                "Altitude (m)": alt,
                "Vitesse (m/s)": round(vitesse, 2),
                "Direction (\u00b0)": round(direction),
                "Direction": self.angle_de_direction(direction),
                "Température (\u00b0C)": round(self.temperature_standard(alt) - 273.15, 2),
                "Pression (kPa)": round(self.pression_standard(alt) / 10, 2)
            })

        df = pd.DataFrame(sorted(meteo_multi_alt, key=lambda x: x['Altitude (m)'], reverse=True))
        st.subheader("📊 Données météorologiques")
        st.dataframe(
            df.style
            .background_gradient(subset=["Vitesse (m/s)"], cmap="Blues")
            .background_gradient(subset=["Température (°C)"], cmap="Reds"),
            width=800
        )
        st.subheader("📈 Graphiques")
        fig_vitesse = px.line(df, x="Altitude (m)", y="Vitesse (m/s)", title="Vitesse du vent", markers=True)
        st.plotly_chart(fig_vitesse, use_container_width=True)

        if all(df["Direction (\u00b0)"].notna()):
            fig_rose = px.bar_polar(df, r="Vitesse (m/s)", theta="Direction (\u00b0)", color="Altitude (m)", title="Tendance du vent", template="plotly_dark")
            st.plotly_chart(fig_rose, use_container_width=True)

        st.subheader("📍 Localisation finale")
        m = folium.Map(location=[self.lat, self.lon], zoom_start=10)
        folium.Marker([self.lat, self.lon], popup=f"Livraison: {self.date_selectionnee} {self.heure_selectionnee.strftime('%H:%M')}", icon=folium.Icon(color="green", icon="truck")).add_to(m)
        st_folium(m, width=700, height=300)

if __name__ == "__main__":
    app = InterfaceStreamlit()
    app.afficher_interface()