import streamlit as st
import numpy as np
from engineering import ConductionWall, NewtonCoolingSystem
from utils.validation import validate_conduction_inputs, validate_cooling_inputs
from utils.plotting import create_cooling_curve_figure

st.set_page_config(
    page_title="Heat Transfer Calculator | Engineering Suite",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 Module B: Heat Transfer Calculator")
st.markdown(
    """
    Perform rigorous steady-state 1D conduction calculations using **Fourier's Law** 
    and transient lumped thermal capacity cooling using **Newton's Law of Cooling**.
    """
)

tab_conduction, tab_cooling = st.tabs([
    "🧱 Section B1: Flat Wall Conduction (Fourier's Law)",
    "⏱️ Section B2: Newton's Law of Cooling (Transient Decay)"
])

# =============================================================================
# TAB 1: Flat Wall Conduction
# =============================================================================
with tab_conduction:
    st.header("1D Steady-State Conduction Across a Flat Wall")
    st.markdown(
        "Calculate the steady-state thermal conduction rate and heat flux through a homogeneous plane wall."
    )

    col_inp, col_res = st.columns([1, 1])

    with col_inp:
        st.subheader("Wall Dimensions & Material Properties")
        k_val = st.number_input(
            "Thermal Conductivity, k (W/(m·K))",
            value=45.0,
            min_value=0.001,
            step=1.0,
            format="%.3f",
            help="Material property describing how readily heat conducts (e.g., Carbon Steel ≈ 45 W/(m·K), Brick ≈ 0.7 W/(m·K))."
        )
        thickness_val = st.number_input(
            "Wall Thickness, L (m)",
            value=0.150,
            min_value=0.0001,
            step=0.010,
            format="%.4f",
            help="The physical distance heat must travel through the wall."
        )
        area_val = st.number_input(
            "Wall Surface Area, A (m²)",
            value=5.0,
            min_value=0.01,
            step=0.5,
            format="%.2f",
            help="The cross-sectional area perpendicular to the direction of heat flow."
        )
        t_hot_val = st.number_input(
            "Hot-Side Temperature, T_hot (°C)",
            value=120.0,
            step=5.0,
            format="%.2f",
            help="Temperature of the hotter boundary surface."
        )
        t_cold_val = st.number_input(
            "Cold-Side Temperature, T_cold (°C)",
            value=25.0,
            step=5.0,
            format="%.2f",
            help="Temperature of the cooler boundary surface."
        )

    # Validate Conduction Inputs
    valid_cond, cond_errors = validate_conduction_inputs(
        thermal_conductivity=k_val,
        thickness=thickness_val,
        area=area_val,
        t_hot=t_hot_val,
        t_cold=t_cold_val
    )

    with col_res:
        st.subheader("Conduction Results")
        if not valid_cond:
            for err in cond_errors:
                st.error(f"❌ **Validation Error:** {err}")
        else:
            wall = ConductionWall(thermal_conductivity=k_val, thickness=thickness_val, area=area_val)
            delta_t = t_hot_val - t_cold_val
            r_th = wall.thermal_resistance
            q_dot_w = wall.heat_rate(t_hot_val, t_cold_val)
            q_dot_kw = q_dot_w / 1000.0
            flux_w_m2 = wall.heat_flux(t_hot_val, t_cold_val)

            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Temperature Difference, ΔT", f"{delta_t:.2f} °C", help="ΔT = T_hot - T_cold")
            m_col2.metric("Thermal Resistance, R_th", f"{r_th:.5f} K/W", help="R_th = L / (k · A)")

            m_col3, m_col4 = st.columns(2)
            m_col3.metric("Heat Rate, Q̇", f"{q_dot_kw:.3f} kW", delta=f"{q_dot_w:.1f} W")
            m_col4.metric("Heat Flux, q''", f"{flux_w_m2:,.1f} W/m²", help="q'' = Q̇ / A")

            st.info(
                f"💡 **Physical Interpretation:** A thermal energy flow of **{q_dot_kw:.3f} kW** passes through the "
                f"**{area_val} m²** wall at steady state, corresponding to an energy intensity of **{flux_w_m2:,.1f} W/m²**."
            )

    with st.expander("📖 Fourier's Law Mathematical Formulation", expanded=False):
        st.latex(r"\dot{Q} = k A \frac{T_{\text{hot}} - T_{\text{cold}}}{L} = \frac{\Delta T}{R_{\text{th}}}")
        st.latex(r"q'' = \frac{\dot{Q}}{A} = k \frac{\Delta T}{L}")
        st.markdown(
            "Where $k$ is thermal conductivity $\\left[\\frac{\\text{W}}{\\text{m}\\cdot\\text{K}}\\right]$, "
            "$A$ is surface area $[\\text{m}^2]$, $L$ is thickness $[\\text{m}]$, and $R_{\\text{th}}$ is conductive resistance $[\\text{K/W}]$."
        )


# =============================================================================
# TAB 2: Newton's Law of Cooling
# =============================================================================
with tab_cooling:
    st.header("Transient Lumped Capacitance Cooling")
    st.markdown(
        "Model the exponential temperature decay of an object exchanging heat with a surrounding ambient reservoir."
    )

    c_col_inp, c_col_res = st.columns([1, 1])

    with c_col_inp:
        st.subheader("Thermal Cooling Parameters")
        t_init_val = st.number_input(
            "Initial Object Temperature, T0 (°C)",
            value=95.0,
            step=5.0,
            format="%.2f",
            help="Starting temperature of the body at time t = 0."
        )
        t_amb_val = st.number_input(
            "Surrounding Ambient Temperature, T_inf (°C)",
            value=22.0,
            step=1.0,
            format="%.2f",
            help="Constant temperature of the surrounding fluid/medium."
        )
        t_target_val = st.number_input(
            "Target Temperature, T_target (°C)",
            value=45.0,
            step=1.0,
            format="%.2f",
            help="Desired threshold temperature."
        )
        cooling_k = st.number_input(
            "Cooling Constant, k_c (1/s)",
            value=0.015,
            min_value=0.0001,
            step=0.001,
            format="%.5f",
            help="Lumped parameter combining convective coefficient, surface area, mass, and specific heat (k_c = h·A / (m·c_p))."
        )

    # Validate Cooling Inputs
    valid_cool, cool_errors = validate_cooling_inputs(
        t_initial=t_init_val,
        t_ambient=t_amb_val,
        t_target=t_target_val,
        cooling_constant=cooling_k
    )

    with c_col_res:
        st.subheader("Cooling Time Results")
        if not valid_cool:
            for err in cool_errors:
                st.error(f"❌ **Physics Error:** {err}")
        else:
            cooling_system = NewtonCoolingSystem(
                t_initial=t_init_val,
                t_ambient=t_amb_val,
                cooling_constant=cooling_k
            )

            try:
                time_to_tgt = cooling_system.time_to_temperature(t_target_val)
                time_mins = time_to_tgt / 60.0

                mc1, mc2 = st.columns(2)
                mc1.metric("Time to Target (Seconds)", f"{time_to_tgt:.2f} s")
                mc2.metric("Time to Target (Minutes)", f"{time_mins:.2f} min")

                st.success(
                    f"🎯 The body cools from **{t_init_val:.1f}°C** down to **{t_target_val:.1f}°C** in "
                    f"**{time_to_tgt:.2f} seconds** ({time_mins:.2f} minutes)."
                )
            except Exception as ex:
                st.error(f"❌ Calculation failure: {ex}")

    # Plot Transient Cooling Curve if inputs are valid
    if valid_cool:
        st.markdown("---")
        st.subheader("📈 Dynamic Temperature vs. Time Decay Curve")
        
        # Adaptive timeline: 1.5x time to target, or at least 5 time constants
        t_max_plot = max(time_to_tgt * 1.5, 5.0 / cooling_k)
        t_vec, temp_vec = cooling_system.generate_cooling_curve(t_max=t_max_plot, points=200)

        fig_cool = create_cooling_curve_figure(
            times=t_vec,
            temperatures=temp_vec,
            t_initial=t_init_val,
            t_ambient=t_amb_val,
            t_target=t_target_val,
            time_target=time_to_tgt
        )
        st.plotly_chart(fig_cool, use_container_width=True)

    with st.expander("📖 Newton's Law of Cooling Analytical Derivation", expanded=False):
        st.markdown("### 1. Differential Equation")
        st.latex(r"\frac{dT}{dt} = -k_c (T - T_{\infty})")
        st.markdown("### 2. Analytical Separation of Variables Solution")
        st.latex(r"\int_{T_0}^{T(t)} \frac{dT}{T - T_{\infty}} = -k_c \int_{0}^{t} dt \implies \ln\left(\frac{T(t) - T_{\infty}}{T_0 - T_{\infty}}\right) = -k_c t")
        st.latex(r"T(t) = T_{\infty} + (T_0 - T_{\infty}) e^{-k_c t}")
        st.markdown("### 3. Exact Time to Reach Target Temperature")
        st.latex(r"t = -\frac{1}{k_c} \ln\left( \frac{T_{\text{target}} - T_{\infty}}{T_0 - T_{\infty}} \right)")
        st.markdown(
            "**Physical Constraint:** The ratio $\\frac{T_{\\text{target}} - T_{\\infty}}{T_0 - T_{\\infty}}$ must be strictly "
            "between $0$ and $1$ for cooling, because the object approaches $T_{\\infty}$ asymptotically and never crosses it."
        )
