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
