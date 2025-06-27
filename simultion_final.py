"""
Ce module définit la classe 'SimulerTrajectoire' pour simuler la trajectoire optimisée d'un parachute guidé (Activement)
à partir d'une position initiale de largage vers une cible GPS precise, en tenant compte de
l'altitude, de la densité de l'air, et du vent réel importé via API.

 Contient :
   - Le calcul de la densité, altitude et vitesse selon des modèles empiriques.
   - L'optimisation convexe de la trajectoire avec (cvxpy).
   - Le dessin 2D, 3D et une animation 3D de la trajectoire.

Auteurs : Syrine Boudef - Wilson David Parra Oliveros - Linda Ghazouani
Date : 26/06/2026
"""

import numpy as np
from importer_vent import import_vent
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.animation import FuncAnimation, PillowWriter
import cvxpy as cvx

class SimulerTrajectoire:
    """
        Classe qui encapsule la simulation de la trajectoire optimisée du parachute
        avec guidage horizontal sous l'effet du vent, vers une cible GPS precise.
        """
    def __init__(self, lat=13, lon=50, N=31, random_range=600):
        """
        Initialise les paramètres physiques et environnementaux du modèle.
        lat, lon : positions de la cible (latitude et longitude)
        N : nombre d'étapes temporelles
        random_range : écart aléatoire autour de la cible pour la position initiale
        """
        self.lat = lat
        self.lon = lon
        print(f"[INIT] Simulation lancée pour : lat = {lat}, lon = {lon}")
        self.N = N
        self.z0 = 1200
        # marge random
        random_lat = np.random.uniform(-random_range, random_range)
        random_lon = np.random.uniform(-random_range, random_range)
        self.x_0 = np.array([[lat + random_lat], [lon + random_lon]])
        #self.x_0 = np.array([[lat+0.01], [lon+0.01]])
        self.cz = 2.256E-5
        self.ce = 4.2559
        self.cf = self.ce / 2 + 1
        self.ch = 1.225
        self.rho0 = self.ch * (1 - self.z0 * self.cz) ** self.ce
        self.rz0 = -7.9
        self.t0 = 0
        self.vz0 = 18.5
        self.psi_0 = 0.

    def calcul_altitude(self, t):
        """ Fonction pour le calcule de l'altitude en fonction du temps t (m)"""
        return 1 / self.cz * (1 - ((((1 - self.z0 * self.cz) ** self.cf) / self.cf / self.cz -
                                    (t - self.t0) * self.rz0 * np.sqrt(self.rho0) / np.sqrt(self.ch)) *
                                   self.cf * self.cz) ** (1 / self.cf))

    def calcul_densite(self, z):
        """ Fonction qui renvoie la densité de l'air en fonction de l'altitude z """
        return self.ch * (1 - z * self.cz) ** self.ce

    def calcul_profil_vitesse(self, z):
        """ Fonction pour le calcul de la vitesse verticale en fonction de la densité d'air à z """
        return self.vz0 * np.sqrt(self.rho0 / self.calcul_densite(z))

    def optimiser_trajectoire(self):
        """
        Fonction principale pour la résolution du problème d'optimisation convexe avec contraintes physiques,
        pour minimiser la distance à la cible.
        """
        W, z_t, time, _ = import_vent(self.lat, self.lon, self.N)
        self.time = time
        self.z_t = z_t

        tf = self.time[-1]
        dt = tf / (self.N - 1)
        z = self.calcul_altitude(self.time)
        v = self.calcul_profil_vitesse(z)

        A = np.eye(2, 2)
        B_p = np.eye(2, 2) * dt * 0.5
        B_m = np.eye(2, 2) * dt * 0.5
        phid_max = 0.14
        u_0 = np.array([[v[0] * np.cos(self.psi_0)], [v[0] * np.sin(self.psi_0)]])

        eps_convergence = 0.01
        alpha_1, alpha_2, alpha_3 = 100, 10, 1

        x = cvx.Variable((2, self.N))
        u = cvx.Variable((2, self.N))
        eps_h = cvx.Variable(nonneg=True)
        u_bar = cvx.Parameter((2, self.N))
        u_init = np.array([v * np.cos(self.psi_0), v * np.sin(self.psi_0)])
        norms = np.linalg.norm(u_init, axis=0)
        norms[norms == 0] = 1e-6
        u_bar.value = np.divide(u_init, norms)

        const = [x[:, [0]] == self.x_0, u[:, [0]] == u_0]
        const += [x[:, [k + 1]] == A @ x[:, [k]] + (B_m @ u[:, [k]] + B_p @ u[:, [k + 1]]) + [W[:, k]]
                  for k in range(self.N - 1)]
        const += [(cvx.norm2(cvx.diff(u, axis=1), axis=0) / dt / v[k])[k] <= phid_max for k in range(self.N - 1)]
        const += [u_bar[:, [k]].T @ u[:, [k]] - v[k] >= -eps_h for k in range(self.N)]
        const += [cvx.norm(u[:, [k]]) - v[k] <= eps_h for k in range(self.N)]

        target = np.array([[self.lat], [self.lon]])
        final_position = cvx.norm(x[:, [-1]] - target)
        final_angle = 2 - u[1, [-1]] / np.linalg.norm(v[-1])
        control_cost = cvx.sum_squares(cvx.norm(cvx.diff(u, axis=1), axis=0) / v[:-1]) / dt
        cost = alpha_1 * final_position + alpha_2 * final_angle + control_cost

        MAX_ITER = 50
        it_cost = np.empty(MAX_ITER)
        X = np.empty((2, self.N, MAX_ITER))

        problem = cvx.Problem(cvx.Minimize(cost), const + [eps_h == 0.1])
        first_stage_converged = False

        for i in range(MAX_ITER):
            s = problem.solve(solver=cvx.ECOS, verbose=True, warm_start=True)
            if u.value is None:
                raise ValueError(f"ECOS n'a pas trouvé de solution à l'itération {i}")

            u_bar.value = np.divide(u.value, np.linalg.norm(u.value, axis=0))

            X[:, :, i] = x.value
            it_cost[i] = cost.value

            if (i > 0 and abs(it_cost[i] - it_cost[i - 1]) < eps_convergence):
                if first_stage_converged:
                    n_iter = i
                    break
                else:
                    cost += alpha_3 * eps_h
                    problem = cvx.Problem(cvx.Minimize(cost), const)
                    first_stage_converged = True

        self.x_star = X[:, :, n_iter]
        self.z_t = z_t
        self.time = time
        self.target = np.array([self.lat, self.lon])
        self.n_iter = n_iter
        return self.x_star, self.calcul_erreur(), (self.x_star[0, -1], self.x_star[1, -1]), self.z_t, self.time

    def calcul_erreur(self):
        """Calcule l'erreur à la cible finale"""
        xf = self.x_star[0, -1]
        yf = self.x_star[1, -1]
        tx, ty = self.target[0], self.target[1]
        return np.sqrt((xf - tx) ** 2 + (yf - ty) ** 2)

    def dessin_trajectoire_2D(self):
        """Affiche et sauvegarde la trajectoire au sol en 2D"""
        filename = f"graph2D_{self.lat:.2f}_{self.lon:.2f}.png"
        plt.figure()
        plt.plot(self.x_star[0, :], self.x_star[1, :], 'b--', label="Trajectoire optimisée")
        plt.plot(self.x_star[0, 0], self.x_star[1, 0], 'go', label="Départ")
        plt.plot(self.x_star[0, -1], self.x_star[1, -1], 'ro', label="Arrivée")
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")
        plt.title("Trajectoire 2D au sol")
        plt.legend()
        plt.grid(True)
        plt.savefig(filename)
        plt.show()
        plt.close()
        return filename

    def dessin_trajectoire_3D(self):
        """Affiche et sauvegarde la trajectoire 3D (avec altitude)"""
        filename = f"graph3D_{self.lat:.2f}_{self.lon:.2f}.png"
        fig = plt.figure()
        ax3d = fig.add_subplot(111, projection='3d')
        ax3d.plot(self.x_star[0, :], self.x_star[1, :], self.z_t, 'b--', label="Trajectoire optimisée")
        ax3d.scatter(self.x_star[0, 0], self.x_star[1, 0], self.z_t[0], color='green', label='Départ')
        ax3d.scatter(self.x_star[0, -1], self.x_star[1, -1], self.z_t[-1], color='red', label='Arrivée')
        ax3d.set_xlabel("x (m)")
        ax3d.set_ylabel("y (m)")
        ax3d.set_zlabel("z (m)")
        ax3d.set_title("Trajectoire 3D")
        ax3d.legend()
        plt.savefig(filename)
        plt.show()
        plt.close()
        return filename

    def animation_trajectoire(self):
        """Crée une animation 3D de la descente et la sauvegarde en .gif"""
        filename = f"trajectoire_{self.lat:.2f}_{self.lon:.2f}.gif"
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        line, = ax.plot([], [], [], lw=2, label="Trajectoire", linestyle=':')
        point, = ax.plot([], [], [], 'ro', label="Parachute")

        x_traj = self.x_star[0, :]
        y_traj = self.x_star[1, :]
        z_traj = self.calcul_altitude(self.time)

        ax.set_xlim(min(x_traj), max(x_traj))
        ax.set_ylim(min(y_traj), max(y_traj))
        ax.set_zlim(0, max(z_traj))
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.set_zlabel("z (m)")
        ax.set_title("Animation 3D de la trajectoire")

        def update(frame):
            line.set_data(x_traj[:frame], y_traj[:frame])
            line.set_3d_properties(z_traj[:frame])
            point.set_data(x_traj[frame:frame + 1], y_traj[frame:frame + 1])
            point.set_3d_properties(z_traj[frame:frame + 1])
            return line, point

        ani = FuncAnimation(fig, update, frames=len(self.time), interval=170, blit=False)
        plt.legend()
        plt.close()  # Pour ne pas afficher dans Streamlit
        ani.save(filename, writer=PillowWriter(fps=5))
        return filename


# Appel de la fonction:
if __name__ == "__main__":
 simulateur = SimulerTrajectoire()
 X, erreur, (xf, yf), z_t, time = simulateur.optimiser_trajectoire()
 simulateur.dessin_trajectoire_2D()
 simulateur.dessin_trajectoire_3D()
 simulateur.animation_trajectoire()