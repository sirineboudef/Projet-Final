import numpy as np
from importer_vent import import_vent
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')
from matplotlib.animation import FuncAnimation, PillowWriter


class ChuteParachuteSimple:
    def __init__(self, lat=47.3388, lon=-81.9141, N=31):
        self.lat = lat
        self.lon = lon
        self.N = N
        self.z0 = 1200
        self.x_0 = np.array([lat + 1000, lon + 1000])  # Position initiale
        self.cz = 2.256E-5
        self.ce = 4.2559
        self.cf = self.ce / 2 + 1
        self.ch = 1.225
        self.rho0 = self.ch * (1 - self.z0 * self.cz) ** self.ce
        self.rz0 = -7.9
        self.t0 = 0
        self.vz0 = 18.5
        self.psi_0 = 0.

        # Chargement des données de vent
        self.W, self.z_t, self.time, _ = import_vent(self.lat, self.lon, self.N)

        # Calcul des paramètres de la chute
        self.altitudes = self.calcul_altitude(self.time)
        self.vitesses = self.calcul_profil_vitesse(self.altitudes)

        # Simulation de la trajectoire sans optimisation
        self.simuler_trajectoire()

    def calcul_altitude(self, t):
        return 1 / self.cz * (1 - ((((1 - self.z0 * self.cz) ** self.cf) / self.cf / self.cz -
                                    (t - self.t0) * self.rz0 * np.sqrt(self.rho0) / np.sqrt(self.ch)) *
                                   self.cf * self.cz) ** (1 / self.cf))

    def calcul_densite(self, z):
        return self.ch * (1 - z * self.cz) ** self.ce

    def calcul_profil_vitesse(self, z):
        return self.vz0 * np.sqrt(self.rho0 / self.calcul_densite(z))

    def simuler_trajectoire(self):
        """Simulation simple de la trajectoire sous l'effet du vent uniquement"""
        dt = self.time[1] - self.time[0]

        # Initialisation
        self.trajectoire = np.zeros((2, self.N))
        self.trajectoire[:, 0] = self.x_0

        # Simulation pas à pas
        for k in range(1, self.N):
            # On ajoute simplement l'effet du vent à la position précédente
            self.trajectoire[:, k] = self.trajectoire[:, k - 1] + self.W[:, k - 1] * dt

            # Petite composante aléatoire pour simuler les turbulences
            self.trajectoire[:, k] += np.random.normal(0, 0.5, 2)

    def dessin_trajectoire_2D(self):
        fig = plt.figure()
        plt.plot(self.trajectoire[0, :], self.trajectoire[1, :], 'b--', label="Trajectoire")
        plt.plot(self.trajectoire[0, 0], self.trajectoire[1, 0], 'go', label="Départ")
        plt.plot(self.trajectoire[0, -1], self.trajectoire[1, -1], 'ro', label="Arrivée")
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")
        plt.title("Trajectoire 2D au sol (sans optimisation)")
        plt.legend()
        plt.grid(True)
        plt.show()

    def dessin_trajectoire_3D(self):
        fig = plt.figure()
        ax3d = fig.add_subplot(111, projection='3d')
        ax3d.plot(self.trajectoire[0, :], self.trajectoire[1, :], self.altitudes, 'b--', label="Trajectoire")
        ax3d.scatter(self.trajectoire[0, 0], self.trajectoire[1, 0], self.altitudes[0], color='green', label='Départ')
        ax3d.scatter(self.trajectoire[0, -1], self.trajectoire[1, -1], self.altitudes[-1], color='red', label='Arrivée')
        ax3d.set_xlabel("x (m)")
        ax3d.set_ylabel("y (m)")
        ax3d.set_zlabel("z (m)")
        ax3d.set_title("Trajectoire 3D (sans optimisation)")
        ax3d.legend()
        plt.show()

    def animation_trajectoire(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        line, = ax.plot([], [], [], lw=2, label="Trajectoire", linestyle=':')
        point, = ax.plot([], [], [], 'ro', label="Parachute")

        x_traj = self.trajectoire[0, :]
        y_traj = self.trajectoire[1, :]
        z_traj = self.altitudes

        ax.set_xlim(min(x_traj) - 100, max(x_traj) + 100)
        ax.set_ylim(min(y_traj) - 100, max(y_traj) + 100)
        ax.set_zlim(0, max(z_traj) + 100)
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.set_zlabel("z (m)")
        ax.set_title("Animation 3D de la chute libre")

        def update(frame):
            line.set_data(x_traj[:frame], y_traj[:frame])
            line.set_3d_properties(z_traj[:frame])
            point.set_data(x_traj[frame:frame + 1], y_traj[frame:frame + 1])
            point.set_3d_properties(z_traj[frame:frame + 1])
            return line, point

        ani = FuncAnimation(fig, update, frames=len(self.time), interval=170, blit=False)
        plt.legend()
        plt.show()


# Appel de la fonction:
simulateur = ChuteParachuteSimple()
simulateur.dessin_trajectoire_2D()
simulateur.dessin_trajectoire_3D()
simulateur.animation_trajectoire()