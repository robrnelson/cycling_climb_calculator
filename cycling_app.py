import streamlit as st
import numpy as np

# --- PHYSICS CONSTANTS ---
GRAVITY = 9.81      # m/s^2
RHO = 1.225         # Air density in kg/m^3 (sea level)
CDA = 0.32          # Drag area in m^2 (typical road climbing position)
BIKE_WEIGHT = 8.0   # kg

st.set_page_config(page_title="Climb Calculator", layout="centered")

st.title("🚵‍♂️ Cycling Climb Calculator")
st.write("Compare the speed and time of two riders on a steady climb.")

# --- COURSE SETTINGS ---
st.header("Course Settings")
distance_km = st.slider("Climb Distance (km)", min_value=0.5, max_value=25.0, value=5.0, step=0.1)
gradient_pct = st.slider("Average Gradient (%)", min_value=0.1, max_value=20.0, value=7.0, step=0.1)
use_aero = st.toggle("Include Air Resistance", value=True)

st.divider()

# --- RIDER SETTINGS (Side-by-side on desktop, stacked on mobile) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔴 Rider A")
    power_a = st.slider("Power (Watts) - A", 100, 600, 250, key="pA")
    weight_a = st.slider("Weight (kg) - A", 40, 120, 70, key="wA")

with col2:
    st.subheader("🔵 Rider B")
    power_b = st.slider("Power (Watts) - B", 100, 600, 300, key="pB")
    weight_b = st.slider("Weight (kg) - B", 40, 120, 80, key="wB")

# --- CALCULATION FUNCTION ---
def calculate_speed_and_time(power, weight, distance, gradient, aero_on):
    total_mass = weight + BIKE_WEIGHT
    theta = np.arctan(gradient / 100.0)
    
    # Gravity component: c * v
    c = total_mass * GRAVITY * np.sin(theta)
    
    if aero_on:
        # Aero component: a * v^3
        a = 0.5 * RHO * CDA
        # Solve the cubic equation: a*v^3 + 0*v^2 + c*v - Power = 0
        roots = np.roots([a, 0, c, -power])
        # Extract the real, positive root (which is the actual speed)
        real_roots = roots[np.isreal(roots)].real
        v_mps = real_roots[real_roots > 0][0] if len(real_roots[real_roots > 0]) > 0 else 0
    else:
        # If no aero, equation is simply c * v = Power
        v_mps = power / c if c > 0 else float('inf')

    # Conversions
    speed_kmh = v_mps * 3.6
    time_hours = distance / speed_kmh if speed_kmh > 0 else 0
    time_minutes = time_hours * 60
    
    return speed_kmh, time_minutes

# --- GET RESULTS ---
speed_a, time_a = calculate_speed_and_time(power_a, weight_a, distance_km, gradient_pct, use_aero)
speed_b, time_b = calculate_speed_and_time(power_b, weight_b, distance_km, gradient_pct, use_aero)

st.divider()

# --- DISPLAY RESULTS ---
st.header("Results")

res_col1, res_col2 = st.columns(2)

with res_col1:
    st.markdown("### 🔴 Rider A")
    st.metric(label="Average Speed", value=f"{speed_a:.1f} km/h")
    st.metric(label="Time to Top", value=f"{int(time_a)}m {int((time_a % 1) * 60)}s")
    st.caption(f"Watts/kg: {(power_a / weight_a):.2f} W/kg")

with res_col2:
    st.markdown("### 🔵 Rider B")
    st.metric(label="Average Speed", value=f"{speed_b:.1f} km/h")
    st.metric(label="Time to Top", value=f"{int(time_b)}m {int((time_b % 1) * 60)}s")
    st.caption(f"Watts/kg: {(power_b / weight_b):.2f} W/kg")

# Time gap calculation
time_diff = abs(time_a - time_b)
diff_str = f"{int(time_diff)}m {int((time_diff % 1) * 60)}s"

if time_a < time_b:
    st.success(f"**Rider A** arrives at the top {diff_str} ahead of Rider B!")
elif time_b < time_a:
    st.info(f"**Rider B** arrives at the top {diff_str} ahead of Rider A!")
else:
    st.warning("It's a dead tie!")
