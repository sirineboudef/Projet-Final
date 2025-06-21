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

    # Paramètres du modèle de chute
    z0 = 1200  # Altitude de largage
    x_0 = np.array([[lat], [lon]])  # coordonnees de largage qui doivent etre similaire au point cible
    cz = 2.256E-5
    ce = 4.2559
    cf = ce / 2 + 1
    ch = 1.225
    rho0 = ch * (1 - z0 * cz) ** ce
    rz0 = -7.9
    t0 = 0
    rho = lambda z: ch * (1 - z * cz) ** ce
    zf = 0
    vz0 = 18.5
    psi_0 = 0.
    z = lambda t: 1 / cz * (
            1 - ((((1 - z0 * cz) ** cf) / cf / cz - (t - t0) * rz0 * np.sqrt(rho0) / np.sqrt(ch)) * cf * cz) ** (
            1 / cf))
    tf = t0 + np.sqrt(ch) / rz0 / np.sqrt(rho0) * (((1 - z0 * cz) ** cf) / cf / cz - ((1 - zf * cz) ** cf) / cf / cz)
    dt = tf / (N - 1)  # constant time step
    time = np.linspace(0, tf, N)

 # Dynamique #
    A = np.eye(2, 2)
    B_p = np.eye(2, 2) * dt * 0.5
    B_m = np.eye(2, 2) * dt * 0.5
    phid_max = 0.14  # maximum rate of turn
    zt = z(time)
    vt = lambda z: vz0 * np.sqrt(rho0 / rho(z))
    v = vt(zt)
    u_0 = np.array([[v[0] * np.cos(psi_0)], [v[0] * np.sin(psi_0)]])