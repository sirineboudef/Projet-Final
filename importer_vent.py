import numpy as np
import requests

def import_vent(lat, lon, hour_index=0, N=31, z0=1200):
    # Constantes pour le calcul de z(t_k)
    cz = 2.256E-5
    ce = 4.2559
    cf = ce / 2 + 1
    ch = 1.225
    rho0 = ch * (1 - z0 * cz) ** ce
    rz0 = -7.9
    t0 = 0

    # Calcul du temps final
    tf = t0 + np.sqrt(ch) / rz0 / np.sqrt(rho0) * (((1 - z0 * cz) ** cf) / cf / cz - ((1 - 0 * cz) ** cf) / cf / cz)
    time = np.linspace(0, tf, N)

    # Altitude z(t_k)
    z_t = 1 / cz * (
                1 - ((((1 - z0 * cz) ** cf) / cf / cz - (time - t0) * rz0 * np.sqrt(rho0) / np.sqrt(ch)) * cf * cz) ** (
                    1 / cf))

    # Récupération des données météo
    altitudes_api = [10, 80, 120, 180]
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=wind_speed_10m,wind_direction_10m,"
        f"wind_speed_80m,wind_direction_80m,"
        f"wind_speed_120m,wind_direction_120m,"
        f"wind_speed_180m,wind_direction_180m"
        f"&timezone=auto"
    )

    response = requests.get(url)
    data = response.json()

    def convert_to_vx_vy(speed_kmh, direction_deg):
        speed_ms = speed_kmh * 1000 / 3600
        angle_rad = np.radians(direction_deg)
        return speed_ms * np.sin(angle_rad), speed_ms * np.cos(angle_rad)

    # Extraction des profils vent
    vx_profiles = []
    vy_profiles = []
    for a in altitudes_api:
        speed = data['hourly'][f'wind_speed_{a}m'][hour_index]
        direction = data['hourly'][f'wind_direction_{a}m'][hour_index]
        vx, vy = convert_to_vx_vy(speed, direction)
        vx_profiles.append(vx)
        vy_profiles.append(vy)

    # Interpolation
    vx_interp = np.interp(z_t, altitudes_api, vx_profiles)
    vy_interp = np.interp(z_t, altitudes_api, vy_profiles)

    W = np.array([vx_interp, vy_interp])
    return W, z_t, time, data