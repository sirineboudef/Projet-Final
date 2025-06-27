"""
simulation_final.py - Simulation de la trajectoire d’un parachute guidé.

Ce module permet :
    - de récupérer les données de vent via l’API Open-Meteo,
    - de modéliser la chute du parachute avec prise en compte de la densité de l’air,
    - d’optimiser la trajectoire via CVXPY,
    - de visualiser les résultats sous forme de graphiques 2D, 3D et animations.

:author: Linda Ghazouani, Syrine Boudef, Wilson David Parra Oliveros
:date: 26/06/2026
"""

# Importations nécessaires
import numpy as np
from trajectoire_colis.importer_vent import import_vent
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.animation import FuncAnimation, PillowWriter
import cvxpy as cvx

def simuler_trajectoire(lat=47.3388, lon=-81.9141, N=31):
    """
    Simule la trajectoire d’un parachute guidé à partir d’un point de largage donné
    en optimisant le contrôle de la direction sous contraintes aérodynamiques et météorologiques.

    Cette fonction :
        - récupère les données de vent via l’API Open-Meteo,
        - construit le modèle de chute verticale avec variation de densité de l'air,
        - optimise la trajectoire en fonction d’un coût combinant distance à la cible,
          effort de contrôle et orientation finale,
        - génère des graphes 2D et 3D,
        - exporte une animation GIF de la trajectoire optimisée.

    :param lat: Latitude de la cible.
    :type lat: float
    :param lon: Longitude de la cible.
    :type lon: float
    :param N: Nombre d’étapes temporelles pour la discrétisation.
    :type N: int

    :return:
        - x_star: Position optimisée du parachute à chaque étape.
        - erreur: Distance finale entre la position d'atterrissage et la cible.
        - (xf, yf): Coordonnées d'atterrissage finales.
        - z_t: Profil d'altitude z(t).
        - time: Vecteur temporel utilisé dans la simulation.
    :rtype: tuple
    """

    W, z_t, time, _ = import_vent(lat, lon, N)
    z0 = 1200
    x_0 = np.array([[lat], [lon]])
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
        1 - ((((1 - z0 * cz) ** cf) / cf / cz - (t - t0) * rz0 * np.sqrt(rho0) / np.sqrt(ch)) * cf * cz) ** (1 / cf))
    tf = t0 + np.sqrt(ch) / rz0 / np.sqrt(rho0) * (((1 - z0 * cz) ** cf) / cf / cz - ((1 - zf * cz) ** cf) / cf / cz)
    dt = tf / (N - 1)
    time = np.linspace(0, tf, N)

    A = np.eye(2, 2)
    B_p = np.eye(2, 2) * dt * 0.5
    B_m = np.eye(2, 2) * dt * 0.5
    phid_max = 0.14
    zt = z(time)
    vt = lambda z: vz0 * np.sqrt(rho0 / rho(z))
    v = vt(zt)
    u_0 = np.array([[v[0] * np.cos(psi_0)], [v[0] * np.sin(psi_0)]])

    eps_h_val = 0.1
    eps_convergence = 0.01
    alpha_1 = 100
    alpha_2 = 10
    alpha_3 = 1

    x = cvx.Variable((2, N))
    u = cvx.Variable((2, N))
    eps_h = cvx.Variable(nonneg=True)
    u_bar = cvx.Parameter((2, N))
    u_init = np.array([v * np.cos(psi_0), v * np.sin(psi_0)])
    u_bar.value = np.divide(u_init, np.linalg.norm(u_init, axis=0))

    const = [x[:, [0]] == x_0]
    const += [u[:, [0]] == u_0]
    const += [x[:, [k + 1]] == A @ x[:, [k]] + (B_m @ u[:, [k]] + B_p @ u[:, [k + 1]]) + [W[:, k]] for k in range(0, N - 1)]
    const += [(cvx.norm2(cvx.diff(u, axis=1), axis=0) / dt / v[k])[k] <= phid_max for k in range(0, N - 1)]
    const += [u_bar[:, [k]].T @ u[:, [k]] - v[k] >= -eps_h for k in range(0, N)]
    const += [cvx.norm(u[:, [k]]) - v[k] <= eps_h for k in range(0, N)]

    target = np.array([[lat], [lon]])
    final_position = cvx.norm(x[:, [-1]] - target)
    final_angle = 2 - u[1, [-1]] / np.linalg.norm(v[-1])
    control_cost = cvx.sum_squares(cvx.norm(cvx.diff(u, axis=1), axis=0) / v[0:N - 1]) / dt
    cost = alpha_1 * final_position + alpha_2 * final_angle + control_cost

    MAX_ITER = 50
    it_final_position = np.empty((MAX_ITER))
    it_final_angle = np.empty((MAX_ITER))
    it_control_cost = np.empty((MAX_ITER))
    it_cost = np.empty((MAX_ITER))
    X = np.empty((2, N, MAX_ITER))
    U = np.empty((2, N, MAX_ITER))
    D = np.empty((N - 1, MAX_ITER))

    problem = cvx.Problem(cvx.Minimize(cost), const + [eps_h == eps_h_val])
    first_stage_converged = False

    print('Iteration number\t Final position\t Final angle\t Control cost\t Total cost')

    for i in range(MAX_ITER):
        s = problem.solve(solver=cvx.ECOS, verbose=True, warm_start=True)
        u_bar.value = np.divide(u.value, np.linalg.norm(u.value, axis=0))

        x_star = x.value
        u_star = u.value
        X[:, :, i] = x_star
        U[:, :, i] = u_star

        it_final_position[i] = final_position.value
        it_final_angle[i] = final_angle.value
        it_control_cost[i] = control_cost.value
        it_cost[i] = cost.value

        print(str(i) + '\t' + '\t' + '\t' + "%10.3E" % it_final_position[i] + '\t' +
              "%10.3E" % it_final_angle[i] + '\t' + "%10.3E" % it_control_cost[i] + '\t' +
              "%10.3E" % it_cost[i])

        if (np.abs(it_cost[i] - it_cost[i - 1]) < eps_convergence) and first_stage_converged:
            print("STAGE 2 CONVERGED AFTER " + str(i) + " ITERATIONS")
            n_iter = i
            xf = X[0, -1, n_iter]
            yf = X[1, -1, n_iter]
            tx, ty = lat, lon
            erreur = np.sqrt((xf - tx) ** 2 + (yf - ty) ** 2)
            print(f"📍 Point d'atterrissage : ({xf:.2f}, {yf:.2f})")
            print(f"🎯 Erreur par rapport à la cible : {erreur:.2f} m")
            break

        if (i > 1) and (np.abs(it_cost[i] - it_cost[i - 1]) < eps_convergence) and not first_stage_converged:
            print("STAGE 1 CONVERGED AFTER " + str(i) + " ITERATIONS")
            cost = cost + alpha_3 * eps_h
            problem = cvx.Problem(cvx.Minimize(cost), const)
            first_stage_converged = True
            n_iter_first = i

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            x_traj = X[0, :, i]
            y_traj = X[1, :, i]
            z_traj = z(time)

            ax.set_xlim(min(x_traj), max(x_traj))
            ax.set_ylim(min(y_traj), max(y_traj))
            ax.set_zlim(0, max(z_traj))
            ax.set_xlabel("x (m)")
            ax.set_ylabel("y (m)")
            ax.set_zlabel("z (m)")
            ax.set_title("Animation 3D de la trajectoire")

            line, = ax.plot([], [], [], lw=2, label="Trajectoire", linestyle=':')
            point, = ax.plot([], [], [], 'ro', label="Parachute")

            def update(frame):
                line.set_data(x_traj[:frame], y_traj[:frame])
                line.set_3d_properties(z_traj[:frame])
                point.set_data(x_traj[frame:frame + 1], y_traj[frame:frame + 1])
                point.set_3d_properties(z_traj[frame:frame + 1])
                return line, point

            ani = FuncAnimation(fig, update, frames=len(time), interval=170, blit=False)
            plt.legend()
            plt.show()

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            line, = ax.plot([], [], [], lw=2)
            x_vals = X[0, :, i]
            y_vals = X[1, :, i]
            z_vals = z_t

            def init():
                line.set_data([], [])
                line.set_3d_properties([])
                ax.set_xlim(np.min(x_vals), np.max(x_vals))
                ax.set_ylim(np.min(y_vals), np.max(y_vals))
                ax.set_zlim(0, np.max(z_vals))
                return line,

            def update(i):
                line.set_data(x_vals[:i], y_vals[:i])
                line.set_3d_properties(z_vals[:i])
                return line,

            ani = FuncAnimation(fig, update, frames=len(z_vals), init_func=init, blit=True)
            ani.save("trajectoire.gif", writer=PillowWriter(fps=5))

    # Graphique 2D
    fig2d = plt.figure()
    plt.plot(X[0, :, n_iter], X[1, :, n_iter], 'b--', label="Trajectoire optimisée")
    plt.plot(X[0, 0, n_iter], X[1, 0, n_iter], 'go', label="Départ")
    plt.plot(X[0, -1, n_iter], X[1, -1, n_iter], 'ro', label="Arrivée")
    plt.xlabel("x (m)")
    plt.ylabel("y (m)")
    plt.title("Trajectoire 2D au sol")
    plt.legend()
    plt.grid(True)
    plt.savefig("graph2D.png")
    plt.close()

    # Graphique 3D
    fig3d = plt.figure()
    ax3d = fig3d.add_subplot(111, projection='3d')
    ax3d.plot(X[0, :, n_iter], X[1, :, n_iter], z_t, 'b--', label="Trajectoire optimisée")
    ax3d.scatter(X[0, 0, n_iter], X[1, 0, n_iter], z_t[0], color='green', label='Départ')
    ax3d.scatter(X[0, -1, n_iter], X[1, -1, n_iter], z_t[-1], color='red', label='Arrivée')
    ax3d.set_xlabel("x (m)")
    ax3d.set_ylabel("y (m)")
    ax3d.set_zlabel("z (m)")
    ax3d.set_title("Trajectoire 3D")
    ax3d.legend()
    plt.savefig("graph3D.png")
    plt.close()

    return x_star, erreur, (xf, yf), z_t, time

# Appel principal pour test local
X, erreur, (xf, yf), z_t, time = simuler_trajectoire()
