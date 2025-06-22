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

    def convert_to_vx_vy(self, speed_kmh, direction_deg):
        speed_ms = speed_kmh * 1000 / 3600
        angle_rad = np.radians(direction_deg)
        return speed_ms * np.sin(angle_rad), speed_ms * np.cos(angle_rad)

    def import_vent(self):
        tf = self.t0 + np.sqrt(self.ch) / self.rz0 / np.sqrt(self.rho0) * (
            ((1 - self.z0 * self.cz) ** self.cf) / self.cf / self.cz - ((1 - 0 * self.cz) ** self.cf) / self.cf / self.cz)
        time = np.linspace(0, tf, self.N)

        z_t = 1 / self.cz * (
            1 - ((((1 - self.z0 * self.cz) ** self.cf) / self.cf / self.cz -
                 (time - self.t0) * self.rz0 * np.sqrt(self.rho0) / np.sqrt(self.ch)) *
                 self.cf * self.cz) ** (1 / self.cf))

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

        vx_profiles = []
        vy_profiles = []
        for a in altitudes_api:
            speed = data['hourly'][f'wind_speed_{a}m'][self.hour_index]
            direction = data['hourly'][f'wind_direction_{a}m'][self.hour_index]
            vx, vy = self.convert_to_vx_vy(speed, direction)
            vx_profiles.append(vx)
            vy_profiles.append(vy)

        vx_interp = np.interp(z_t, altitudes_api, vx_profiles)
        vy_interp = np.interp(z_t, altitudes_api, vy_profiles)

        W = np.array([vx_interp, vy_interp])
        return W, z_t, time, data


def import_vent(lat, lon, hour_index=0, N=31, z0=1200):
    return ImportVent(lat, lon, hour_index, N, z0).import_vent()