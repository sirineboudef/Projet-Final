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
