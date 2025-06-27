import numpy as np
from importer_vent import import_vent
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.animation import FuncAnimation, PillowWriter
import cvxpy as cvx
import numpy as np
import matplotlib

class Chute_livre:
    def __init__(self):
        # Constantes physiques
        self.g = 9.81  # Accélération gravitationnelle
        self.dt = 0.05  # Pas de temps

        # Paramètres initiaux
        self.altitude_initiale = 100
        self.angle = 10  # Angle en degrés
        self.v0x = 5.0  # Vitesse horizontale initiale
        self.v0z = 5.0  # Vitesse verticale initiale

        # État du système
        self.x = 0
        self.z = self.altitude_initiale
        self.vz = self.v0z

        # Historique des positions
        self.x_list = [self.x]
        self.z_list = [self.z]

        # Configuration de la figure
        self.fig = plt.figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Éléments graphiques
        self.point, = self.ax.plot([], [], [], 'ro', markersize=10)
        self.trace, = self.ax.plot([], [], [], 'b--', linewidth=2)

        self.setup_axes()

    def setup_axes(self):
        """Configure les axes du graphique"""
        self.ax.set_xlim(0, 15)
        self.ax.set_ylim(1, -1)  # Peu de variation en y
        self.ax.set_zlim(2, self.altitude_initiale + 0)
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')
        self.ax.set_title('largagé initial du colis(chute livre)')

    def init_animation(self):
        """Initialisation de l'animation"""
        self.point.set_data([], [])
        self.point.set_3d_properties([])
        self.trace.set_data([], [])
        self.trace.set_3d_properties([])
        return self.point, self.trace

    def update_system(self):
        """Mise à jour de la position et vitesse"""
        self.x += self.v0x * self.dt
        self.z += self.vz * self.dt
        self.vz -= self.g * self.dt

        self.x_list.append(self.x)
        self.z_list.append(self.z)

    def update_animation(self, frame):
        """Fonction de mise à jour pour l'animation"""
        self.update_system()

        # Mise à jour du point
        self.point.set_data([self.x], [0])
        self.point.set_3d_properties([self.z])

        # Mise à jour de la trace
        self.trace.set_data(self.x_list, np.zeros_like(self.x_list))
        self.trace.set_3d_properties(self.z_list)

        # Arrêter quand on touche le sol
        if self.z <= 0:
            self.ani.event_source.stop()

        return self.point, self.trace

    def run_simulation(self):
        """Lance la simulation"""
        self.ani = FuncAnimation(
            self.fig,
            self.update_animation,
            frames=200,
            init_func=self.init_animation,
            interval=50,
            blit=True
        )
        plt.tight_layout()
        plt.show()


# Utilisation de la classe
if __name__ == "__main__":
    simulation = Chute_livre()
    simulation.run_simulation()
