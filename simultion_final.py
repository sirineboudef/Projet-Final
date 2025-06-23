import numpy as np
from importer_vent import import_vent
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.animation import FuncAnimation, PillowWriter
import cvxpy as cvx

class SimulationTrajectoire:
    def __init__(self, lat=47.3388, lon=-81.9141, N=31):
        self.lat = lat
        self.lon = lon
        self.N = N
        self.z0 = 1200
        self.x_0 = np.array([[lat+1000], [lon+1000]])
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
        return 1 / self.cz * (1 - ((((1 - self.z0 * self.cz) ** self.cf) / self.cf / self.cz -
                                    (t - self.t0) * self.rz0 * np.sqrt(self.rho0) / np.sqrt(self.ch)) *
                                   self.cf * self.cz) ** (1 / self.cf))

    def calcul_densite(self, z):
        return self.ch * (1 - z * self.cz) ** self.ce

    def calcul_profil_vitesse(self, z):
        return self.vz0 * np.sqrt(self.rho0 / self.calcul_densite(z))

    def simuler_trajectoire(self):
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
        xf = self.x_star[0, -1]
        yf = self.x_star[1, -1]
        tx, ty = self.target[0], self.target[1]
        return np.sqrt((xf - tx) ** 2 + (yf - ty) ** 2)

    def dessin_trajectoire_2D(self):
        fig = plt.figure()
        plt.plot(self.x_star[0, :], self.x_star[1, :], 'b--', label="Trajectoire optimisée")
        plt.plot(self.x_star[0, 0], self.x_star[1, 0], 'go', label="Départ")
        plt.plot(self.x_star[0, -1], self.x_star[1, -1], 'ro', label="Arrivée")
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")
        plt.title("Trajectoire 2D au sol")
        plt.legend()
        plt.grid(True)
        plt.savefig("graph2D.png")
        plt.show()

    def dessin_trajectoire_3D(self):
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
        plt.savefig("graph3D.png")
        plt.show()

