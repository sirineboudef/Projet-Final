#Importations necessaires
import numpy as np
from importer_vent import import_vent# <== fichier où se trouve ta fonction précédente
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Pour ouvrir une fenêtre interactive
from matplotlib.animation import FuncAnimation, PillowWriter

# Definition de la fonction
def simuler_trajectoire(lat=47.3388, lon=-81.9141, N=31):

    # --- Importation des vents + profil z(t) ---

    W, z_t, time,_ = import_vent(lat, lon, N)