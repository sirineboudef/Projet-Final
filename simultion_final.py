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

