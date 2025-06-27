"""
Ce module définit la classe `ImportVent`.

 Responsable de :
    - récupérer les données de vent en temps réel via l’API Open-Meteo,
    - interpoler les composantes du vent en fonction de l'altitude et du temps,
    - renvoyer le champ de vent utilisé dans l’optimisation de trajectoire.

Auteurs : Linda Ghazouani - Syrine Boudef - Wilson David Parra Oliveros

Date : 26/06/2026
"""

# Importation des bibliotheques necessaires
import numpy as np
import requests

class ImportVent:
    """
       Classe qui permet l'interpolation des vents à différentes altitudes à partir de l'API Open-météo.

       Attributs principaux :
           - lat, lon : coordonnées GPS de la zone cible (latitude et longitude)
           - hour_index : index d'heure dans les données de l'API (ex: 0 pour l'heure actuelle)
           - N : Nombre d'etapes temporelle
           - z0 : altitude d'ouverture du parachute

       La classe fournit :
           - le champ de vent interpolé W (vx, vy)
           - le profil d'altitude z(t)
           - le vecteur temps associé
           - les données brutes de l'API météo
       """
    def __init__(self, lat, lon, hour_index=0, N=31, z0=1200):
        self.lat = lat
        self.lon = lon
        self.hour_index = hour_index
        self.N = N
        self.z0 = z0
        # Constantes atmosphériques
        self.cz = 2.256E-5
        self.ce = 4.2559
        self.cf = self.ce / 2 + 1
        self.ch = 1.225
        self.rho0 = self.ch * (1 - self.z0 * self.cz) ** self.ce
        self.rz0 = -7.9
        self.t0 = 0

    def convert_to_vx_vy(self, speed_kmh, direction_deg):
        """
        Convertit une vitesse et une direction en composantes cartésiennes (vx, vy).
        """
        speed_ms = speed_kmh * 1000 / 3600
        angle_rad = np.radians(direction_deg)
        return speed_ms * np.sin(angle_rad), speed_ms * np.cos(angle_rad)

    def import_vent(self):
        """
        Récupère les données de vent depuis l'API et les interpole selon l'altitude.
        """
        # Profil temporel
        tf = self.t0 + np.sqrt(self.ch) / self.rz0 / np.sqrt(self.rho0) * (
            ((1 - self.z0 * self.cz) ** self.cf) / self.cf / self.cz - ((1 - 0 * self.cz) ** self.cf) / self.cf / self.cz)
        time = np.linspace(0, tf, self.N)
        # Profil d'altitude z(t)
        z_t = 1 / self.cz * (
            1 - ((((1 - self.z0 * self.cz) ** self.cf) / self.cf / self.cz -
                 (time - self.t0) * self.rz0 * np.sqrt(self.rho0) / np.sqrt(self.ch)) *
                 self.cf * self.cz) ** (1 / self.cf))
        # Requête API open-meteo
        altitudes_api = [10, 80, 120, 180]
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={self.lat}&longitude={self.lon}"
            f"&hourly=wind_speed_10m,wind_direction_10m,"
            f"wind_speed_80m,wind_direction_80m,"
            f"wind_speed_120m,wind_direction_120m,"
            f"wind_speed_180m,wind_direction_180m"
            f"&timezone=auto"
        )

        response = requests.get(url)
        data = response.json()
        # Récupération des vitesses et directions à 4 altitudes
        vx_profiles = []
        vy_profiles = []
        for a in altitudes_api:
            speed = data['hourly'][f'wind_speed_{a}m'][self.hour_index]
            direction = data['hourly'][f'wind_direction_{a}m'][self.hour_index]
            vx, vy = self.convert_to_vx_vy(speed, direction)
            vx_profiles.append(vx)
            vy_profiles.append(vy)
        # Interpolation du vent sur z(t)
        vx_interp = np.interp(z_t, altitudes_api, vx_profiles)
        vy_interp = np.interp(z_t, altitudes_api, vy_profiles)

        W = np.array([vx_interp, vy_interp])
        return W, z_t, time, data


def import_vent(lat, lon, hour_index=0, N=31, z0=1200):
    """
    Interface simple pour utiliser la classe ImportVent à partir d'un appel direct.
    """
    return ImportVent(lat, lon, hour_index, N, z0).import_vent()