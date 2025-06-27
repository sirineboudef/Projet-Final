"""
interface_streamlit.py - Interface utilisateur Streamlit pour la simulation de livraison par parachute guidé.

Ce module propose une interface interactive qui permet à l'utilisateur de :
    - sélectionner un point de livraison sur une carte,
    - consulter les données météorologiques en temps réel à plusieurs altitudes,
    - visualiser graphiquement la météo (courbes, roses des vents),
    - lancer une simulation aérodynamique complète de la trajectoire d'un parachute,
    - observer les résultats sous forme de cartes, d'images et d'animations 3D.

:author: Linda Ghazouani, Syrine Boudef, Wilson David Parra Oliveros
:date: 26/06/2026
"""

import streamlit as st
from streamlit_folium import st_folium
import folium
import pytz
import pandas as pd


def temperature_standard(h):
    """
    Calcule la température standard en fonction de l'altitude (modèle ISA).

    :param h: Altitude en mètres.
    :type h: float
    :return: Température en Kelvin.
    :rtype: float
    """
    T0 = 288.15
    lapse_rate = 0.0065
    return T0 - lapse_rate * h

def pression_standard(h):
    """
    Calcule la pression atmosphérique standard selon l'altitude (modèle barométrique ISA).

    :param h: Altitude en mètres.
    :type h: float
    :return: Pression en hPa.
    :rtype: float
    """
    T0 = 288.15
    P0 = 1013.25
    lapse_rate = 0.0065
    g = 9.80665
    M = 0.0289644
    R = 8.31447
    return P0 * (1 - (lapse_rate * h) / T0) ** ((g * M) / (R * lapse_rate))

def set_background_image():
    """
    Applique une image GIF en fond de page via CSS pour personnaliser l'interface Streamlit.
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

def angle_to_direction(angle):
    """
    Convertit un angle en degrés vers une direction cardinale (Nord, Sud, etc.).

    :param angle: Angle en degrés.
    :type angle: float
    :return: Direction cardinale correspondante.
    :rtype: str
    """
    directions = ['Nord', 'Nord-Est', 'Est', 'Sud-Est', 'Sud', 'Sud-Ouest', 'Ouest', 'Nord-Ouest']
    idx = int((angle + 22.5) % 360 / 45)
    return directions[idx]