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
from simulation_trajectoire_parachute import *


class TraitementMeteo:
    @staticmethod
    def temperature_standard(h):
        T0 = 288.15
        taux_refroidissement = 0.0065
        return T0 - taux_refroidissement * h

    @staticmethod
    def pression_standard(h):
        T0 = 288.15
        P0 = 1013.25
        taux_refroidissement = 0.0065
        g = 9.80665
        M = 0.0289644
        R = 8.31447
        return P0 * (1 - (taux_refroidissement * h) / T0) ** ((g * M) / (R * taux_refroidissement))

    @staticmethod
    def angle_vers_direction(angle):
        directions = ['Nord', 'Nord-Est', 'Est', 'Sud-Est', 'Sud', 'Sud-Ouest', 'Ouest', 'Nord-Ouest']
        idx = int((angle + 22.5) % 360 / 45)
        return directions[idx]


class RecuperateurMeteo:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.reponse = None

    def recuperer(self):
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={self.lat}&longitude={self.lon}"
            f"&hourly=wind_speed_10m,wind_direction_10m,"
            f"wind_speed_80m,wind_direction_80m,"
            f"wind_speed_120m,wind_direction_120m,"
            f"wind_speed_180m,wind_direction_180m"
            f"&timezone=auto"
        )
        try:
            self.reponse = requests.get(url).json()
            return self.reponse
        except Exception as e:
            st.error("Erreur lors de la récupération des données météo.")
            st.exception(e)
            return None


class AffichageMeteo:
    def __init__(self, lat, lon, reponse):
        self.lat = lat
        self.lon = lon
        self.reponse = reponse
        self.traitement = TraitementMeteo()

    def afficher(self):
        heures_disponibles = self.reponse["hourly"]["time"]
        heures_disponibles_dt = [datetime.fromisoformat(h) for h in heures_disponibles]

        st.subheader("🗓️ Sélection de la date de livraison")
        date_min = datetime.now().date()
        date_max = (datetime.now() + timedelta(days=7)).date()
        date_selectionnee = st.date_input("Choisissez la date de livraison", min_value=date_min, max_value=date_max, value=date_min)

        heures_du_jour = [h for h in heures_disponibles_dt if h.date() == date_selectionnee]

        if heures_du_jour:
            heure_selectionnee = st.selectbox("Sélectionnez l'heure", heures_du_jour)
            index_horaire = heures_disponibles_dt.index(heure_selectionnee)

            altitudes = [10, 80, 120, 180]
            donnees_meteo = []

            for alt in altitudes:
                vitesse = self.reponse["hourly"].get(f"wind_speed_{alt}m", [None])[index_horaire]
                direction = self.reponse["hourly"].get(f"wind_direction_{alt}m", [None])[index_horaire]

                donnees_meteo.append({
                    "Altitude (m)": alt,
                    "Vitesse (m/s)": round(vitesse, 2) if vitesse else None,
                    "Direction (°)": round(direction) if direction else None,
                    "Direction": self.traitement.angle_vers_direction(direction) if direction else None,
                    "Température (°C)": round(self.traitement.temperature_standard(alt) - 273.15, 2),
                    "Pression (kPa)": round(self.traitement.pression_standard(alt) / 10, 2)
                })

            donnees_meteo.sort(key=lambda x: x['Altitude (m)'], reverse=True)
            df_meteo = pd.DataFrame(donnees_meteo)

            st.subheader("📊 Données météorologiques")
            st.dataframe(
                df_meteo.style
                .background_gradient(subset=["Vitesse (m/s)"], cmap="Blues")
                .background_gradient(subset=["Température (°C)"], cmap="Reds"),
                width=800
            )

            st.subheader("📈 Visualisations")
            fig_vitesse = px.line(
                df_meteo, x="Altitude (m)", y="Vitesse (m/s)", title="Vitesse du vent par altitude",
                markers=True, color_discrete_sequence=["#3498DB"]
            )
            st.plotly_chart(fig_vitesse, use_container_width=True)

            if all(df_meteo["Direction (°)"].notna()):
                fig_rose = px.bar_polar(
                    df_meteo, r="Vitesse (m/s)", theta="Direction (°)", color="Altitude (m)",
                    title="Tendance du vent", template="plotly_dark",
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig_rose, use_container_width=True)

            return date_selectionnee, heure_selectionnee
        else:
            st.warning("Aucune donnée disponible pour cette date.")
            return None, None


class LanceurSimulation:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def lancer(self):
        x_star, erreur, (xf, yf), z_t, time = simuler_trajectoire(lat=self.lat, lon=self.lon)
        st.write(f"📍 Point d'atterrissage : ({xf:.2f}, {yf:.2f})")
        st.write(f"🎯 Erreur par rapport à la cible : {erreur:.2f} m")
        st.image("trajectoire.gif", caption="Animation 3D de la trajectoire")
        st.image("graph2D.png", caption="📉 Trajectoire au sol (2D)")
        st.image("graph3D.png", caption="📊 Trajectoire complète (3D)")


class InterfaceUtilisateur:
    @staticmethod
    def definir_fond():
        fond = '''<style>.stApp {background-image: url("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzIxcWV6OHVhb25yNDB6NXBoY29uaGU3a2tnMWFvdDRxbXQ5Z2lsZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7qDKdHAqamtq0uBi/giphy.gif"); background-size: cover; background-position: center; background-repeat: no-repeat;}</style>'''
        st.markdown(fond, unsafe_allow_html=True)

    @staticmethod
    def demarrer():
        st.set_page_config(layout="centered", page_title="Météo Livraison Drone")
        InterfaceUtilisateur.definir_fond()
        st.title("🌍 Sélectionnez un point de livraison sur la carte")
        m = folium.Map(location=[48.85, 2.35], zoom_start=4)
        folium.LatLngPopup().add_to(m)
        st.markdown('<p style="color:blue">Cliquez sur la carte pour sélectionner les coordonnées.</p>', unsafe_allow_html=True)
        return st_folium(m, width=700, height=500)


class Application:
    def executer(self):
        donnees_carte = InterfaceUtilisateur.demarrer()

        if donnees_carte and donnees_carte.get("last_clicked"):
            lat = donnees_carte["last_clicked"]["lat"]
            lon = donnees_carte["last_clicked"]["lng"]
            st.success(f"📍 Coordonnées sélectionnées : {lat:.4f}, {lon:.4f}")

            meteo = RecuperateurMeteo(lat, lon)
            reponse = meteo.recuperer()
            if reponse:
                affichage = AffichageMeteo(lat, lon, reponse)
                date_livraison, heure_livraison = affichage.afficher()

                if st.button("🚀 Lancer la simulation"):
                    LanceurSimulation(lat, lon).lancer()
        else:
            st.info("Veuillez sélectionner un point sur la carte pour commencer.")


if __name__ == "__main__":
    Application().executer()
