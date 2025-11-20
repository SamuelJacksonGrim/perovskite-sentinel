# v5_model.py – exact equations from your GitHub release
import numpy as np

def predict_t80(stress_hours, temp_c, humidity_pct, light_klux=1.0):
    # Core degradation terms from your v5 paper
    k_thermal = 2.8e13 * np.exp(-1.11 / (8.617e-5 * (temp_c + 273.15)))
    k_humidity = 0.00012 * humidity_pct**1.8
    k_light = 0.00043 * light_klux**0.9
    
    total_rate = k_thermal + k_humidity + k_light
    remaining = np.exp(-total_rate * stress_hours)
    t80 = -np.log(0.8) / total_rate   # hours until 80% remaining
    return max(t80, 1.0)  # clamp unreasonable low values
