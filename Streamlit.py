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
