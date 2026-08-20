import streamlit as st
import numpy as np
import pandas as pd
from engineering import Fluid, Pipe, PREDEFINED_FLUIDS, friction_factor_colebrook
from utils.validation import validate_pipe_inputs
from utils.plotting import create_pressure_drop_figure

st.set_page_config(
    page_title="Pipe Flow Analyser | Engineering Suite",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 Module A: Pipe Flow Analyser")
st.markdown(
    """
    Evaluate internal single-phase hydraulic flow through cylindrical conduits using the **Darcy-Weisbach** framework 
    and the implicit **Colebrook-White** turbulent friction solver.
    """
)

# -----------------------------------------------------------------------------
# Sidebar: Fluid Properties & Pipe Geometry Inputs
# -----------------------------------------------------------------------------
st.sidebar.header("🔧 Configuration & Inputs")

# Fluid Selector
st.sidebar.subheader("1. Fluid Properties")
fluid_option = st.sidebar.selectbox(
    "Select Fluid Type",
    options=list(PREDEFINED_FLUIDS.keys()) + ["User-Defined Fluid"],
    help="Select a standard reference fluid or enter custom density and viscosity."
)

if fluid_option in PREDEFINED_FLUIDS:
    base_fluid = PREDEFINED_FLUIDS[fluid_option]
    st.sidebar.caption("⚠️ *Representative engineering values at standard ambient conditions.*")
    density = st.sidebar.number_input(
        "Density, ρ (kg/m³)",
        value=float(base_fluid.density),
        min_value=0.001,
        format="%.3f",
        help="Fluid mass per unit volume."
    )
    viscosity = st.sidebar.number_input(
        "Dynamic Viscosity, μ (Pa·s)",
        value=float(base_fluid.dynamic_viscosity),
        min_value=1e-7,
        format="%.6e",
        help="Dynamic (absolute) viscosity in Pa·s (or N·s/m²)."
    )
    fluid_name = fluid_option
else:
    fluid_name = st.sidebar.text_input("Custom Fluid Name", value="Custom Synthetic Fluid")
    density = st.sidebar.number_input("Density, ρ (kg/m³)", value=1000.0, min_value=0.001, format="%.2f")
    viscosity = st.sidebar.number_input("Dynamic Viscosity, μ (Pa·s)", value=0.001, min_value=1e-7, format="%.6e")

# Pipe Geometry Inputs
st.sidebar.subheader("2. Pipe Geometry & Flow Conditions")
diameter = st.sidebar.number_input(
    "Internal Pipe Diameter, D (m)",
    value=0.050,
    min_value=0.001,
    step=0.005,
    format="%.4f",
    help="Internal inside diameter available for fluid flow."
)
length = st.sidebar.number_input(
    "Pipe Length, L (m)",
    value=100.0,
    min_value=0.1,
    step=10.0,
    format="%.2f",
    help="Total linear length of the straight pipe conduit."
)
roughness = st.sidebar.number_input(
    "Absolute Surface Roughness, ε (m)",
    value=0.000045,
    min_value=0.0,
    step=0.00001,
    format="%.6f",
    help="Equivalent sand-grain surface roughness height (Commercial steel ~ 0.000045 m)."
)
flow_rate = st.sidebar.number_input(
    "Volumetric Flow Rate, Q (m³/s)",
    value=0.0040,
    min_value=0.0,
    step=0.0005,
    format="%.5f",
    help="Volumetric flow rate of the fluid traveling through the pipe."
)

# -----------------------------------------------------------------------------
# Input Validation & Execution
# -----------------------------------------------------------------------------
is_valid, validation_errors = validate_pipe_inputs(
    diameter=diameter,
    length=length,
    roughness=roughness,
    flow_rate=flow_rate,
    density=density,
    viscosity=viscosity
)

if not is_valid:
    for err in validation_errors:
        st.error(f"❌ **Input Error:** {err}")
    st.stop()

# Instantiate Core OOP Models
fluid_obj = Fluid(name=fluid_name, density=density, dynamic_viscosity=viscosity)
pipe_obj = Pipe(diameter=diameter, length=length, roughness=roughness)

# Execute Hydraulic Calculations
area = pipe_obj.cross_sectional_area
velocity = pipe_obj.velocity(flow_rate)
reynolds = pipe_obj.reynolds_number(flow_rate, fluid_obj)
regime = pipe_obj.flow_regime(reynolds)
friction_factor = pipe_obj.friction_factor(reynolds)
pressure_drop_pa = pipe_obj.pressure_drop(flow_rate, fluid_obj)
pressure_drop_kpa = pressure_drop_pa / 1000.0
head_loss_m = pipe_obj.head_loss(flow_rate, fluid_obj)

# -----------------------------------------------------------------------------
# Display KPI Results Metric Cards
# -----------------------------------------------------------------------------
st.subheader("📊 Primary Hydraulic Flow Results")

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Mean Velocity, V", value=f"{velocity:.3f} m/s", help="Average fluid velocity across cross-section: V = Q / A")
col2.metric(label="Reynolds Number, Re", value=f"{reynolds:,.0f}", help="Ratio of inertial to viscous forces: Re = ρVD / μ")
col3.metric(label="Flow Regime", value=regime, help="Laminar (<2300), Transitional (2300-4000), or Turbulent (>4000)")
col4.metric(label="Darcy Friction Factor, f", value=f"{friction_factor:.5f}" if flow_rate > 0 else "0.00000", help="Darcy friction coefficient (dimensionless)")

col5, col6, col7, col8 = st.columns(4)
col5.metric(label="Cross-Sectional Area, A", value=f"{area:.5f} m²")
col6.metric(label="Relative Roughness, ε/D", value=f"{pipe_obj.relative_roughness:.6f}")
col7.metric(label="Pressure Drop, ΔP", value=f"{pressure_drop_kpa:.3f} kPa", delta=f"{pressure_drop_pa:.1f} Pa")
col8.metric(label="Head Loss, h_f", value=f"{head_loss_m:.3f} m", help="Frictional head loss in meters of fluid column")

if regime == "Transitional":
    st.warning("⚠️ **Flow in Transitional Regime (2300 ≤ Re ≤ 4000):** Flow behavior oscillates intermittently between laminar and turbulent states. Friction factor predictions have higher uncertainty.")

# -----------------------------------------------------------------------------
# Interactive Visualization: ΔP vs Flow Rate
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📈 Performance Characteristic: Pressure Drop vs. Flow Rate")

# Generate Flow Rate Sweep Array around operating point
if flow_rate > 0:
    max_q = max(flow_rate * 2.0, 0.01)
else:
    max_q = 0.02

q_sweep = np.linspace(0.0001, max_q, 100)
dp_sweep_kpa = np.array([pipe_obj.pressure_drop(q_val, fluid_obj) / 1000.0 for q_val in q_sweep])

fig_dp = create_pressure_drop_figure(
    flow_rates=q_sweep,
    pressure_drops_kpa=dp_sweep_kpa,
    current_q=flow_rate,
    current_dp_kpa=pressure_drop_kpa,
    fluid_name=fluid_obj.name
)
st.plotly_chart(fig_dp, use_container_width=True)

# -----------------------------------------------------------------------------
# CSV Dataset Export
# -----------------------------------------------------------------------------
# Construct tabular dataset for the flow rate sweep
export_records = []
for q_val in q_sweep:
    v_val = pipe_obj.velocity(q_val)
    re_val = pipe_obj.reynolds_number(q_val, fluid_obj)
    f_val = pipe_obj.friction_factor(re_val)
    dp_val = pipe_obj.pressure_drop(q_val, fluid_obj)
    hf_val = pipe_obj.head_loss(q_val, fluid_obj)
    export_records.append({
        "flow_rate_m3_s": round(q_val, 6),
        "velocity_m_s": round(v_val, 4),
        "reynolds_number": round(re_val, 2),
        "friction_factor": round(f_val, 6),
        "pressure_drop_Pa": round(dp_val, 2),
        "pressure_drop_kPa": round(dp_val / 1000.0, 4),
        "head_loss_m": round(hf_val, 4)
    })

export_df = pd.DataFrame(export_records)
csv_buffer = export_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Download Calculated Hydraulic Curve Dataset (CSV)",
    data=csv_buffer,
    file_name=f"pipe_flow_analysis_{fluid_obj.name.replace(' ', '_').lower()}.csv",
    mime="text/csv",
    help="Click to export the computed flow rate sweep table as a CSV file."
)

# -----------------------------------------------------------------------------
# Theory & Mathematical Derivations Expander
# -----------------------------------------------------------------------------
with st.expander("📖 Engineering Equations & Governing Principles", expanded=False):
    st.markdown("### 1. Cross-Sectional Area and Velocity")
    st.latex(r"A = \frac{\pi D^2}{4}, \qquad V = \frac{Q}{A}")
    st.markdown(
        "Where $D$ is the inside pipe diameter (m), $A$ is the cross-sectional area (m²), "
        "$Q$ is volumetric flow rate (m³/s), and $V$ is mean fluid velocity (m/s)."
    )

    st.markdown("### 2. Reynolds Number & Flow Classification")
    st.latex(r"Re = \frac{\rho V D}{\mu} = \frac{V D}{\nu}")
    st.markdown(
        "* **Laminar Regime ($Re < 2300$):** Viscous forces dominate, characterized by smooth, parallel streamlines.\n"
        "* **Transitional Regime ($2300 \le Re \le 4000$):** Streamlines fluctuate unpredictably.\n"
        "* **Turbulent Regime ($Re > 4000$):** Inertial forces dominate, resulting in chaotic eddies and transverse mixing."
    )

    st.markdown("### 3. Darcy Friction Factor ($f$)")
    st.markdown("For laminar flow:")
    st.latex(r"f = \frac{64}{Re}")
    st.markdown("For turbulent flow, solved via the implicit **Colebrook-White equation**:")
    st.latex(r"\frac{1}{\sqrt{f}} = -2 \log_{10} \left( \frac{\varepsilon / D}{3.7} + \frac{2.51}{Re \sqrt{f}} \right)")
    st.markdown(
        "Because $f$ appears on both sides inside square roots and logarithms, the suite applies Brent's root-finding algorithm "
        "initialized with Haaland's explicit approximation."
    )

    st.markdown("### 4. Darcy-Weisbach Pressure Drop & Head Loss")
    st.latex(r"\Delta P = f \left( \frac{L}{D} \right) \left( \frac{\rho V^2}{2} \right), \qquad h_f = \frac{\Delta P}{\rho g}")
    st.markdown("Where $L$ is length (m), $\\rho$ is density (kg/m³), and $g = 9.81\\text{ m/s}^2$.")
