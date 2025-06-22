import numpy as np
import requests

class ImportVent:
    def __init__(self, lat, lon, hour_index=0, N=31, z0=1200):
        self.lat = lat
        self.lon = lon
        self.hour_index = hour_index
        self.N = N
        self.z0 = z0

        self.cz = 2.256E-5
        self.ce = 4.2559
        self.cf = self.ce / 2 + 1
        self.ch = 1.225
        self.rho0 = self.ch * (1 - self.z0 * self.cz) ** self.ce
        self.rz0 = -7.9
        self.t0 = 0
