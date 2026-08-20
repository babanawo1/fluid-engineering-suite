import streamlit as st

st.set_page_config(
    page_title="Fluid Flow & Heat Transfer Engineering Suite",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Header & Introduction
# -----------------------------------------------------------------------------
st.title("⚙️ Fluid Flow & Heat Transfer Engineering Suite")
st.subheader("Interactive engineering calculations, visualization, and petrophysical data analysis")

st.markdown(
    """
    Welcome to the **Fluid Flow & Heat Transfer Engineering Suite**, a unified computational application 
    engineered for mechanical, chemical, and petroleum engineering calculations. 

    This software integrates **object-oriented numerical modelling**, **rigorous engineering boundary validation**, 
    and **interactive visual analytics** across three core engineering disciplines.
    """
)

st.markdown("---")

# -----------------------------------------------------------------------------
# Module Highlights (3-Column Layout)
# -----------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🌊 Module A")
    st.markdown("#### Pipe Flow Analyser")
    st.markdown(
        """
        - **Hydraulic Solver**: Single-phase pressure drop ($\Delta P$) and head loss ($h_f$) in closed conduits.
        - **Governing Principles**: Darcy-Weisbach formulation with explicit & implicit Colebrook-White root-solving.
        - **Fluid Database**: Predefined fluid library (Water, Air, Crude Oil) or fully custom thermodynamic properties.
        - **Interactive Curves**: Real-time $\Delta P \text{ vs } Q$ performance curves and CSV dataset export.
        """
    )
    st.page_link("pages/1_Pipe_Flow_Analyser.py", label="Open Pipe Flow Analyser", icon="🌊")

with col2:
    st.markdown("### 🔥 Module B")
    st.markdown("#### Heat Transfer Calculator")
    st.markdown(
        """
        - **1D Conduction**: Fourier's Law calculator for steady-state heat rate ($\dot{Q}$) and heat flux ($q''$).
        - **Transient Cooling**: Newton's Law of Cooling lumped thermal capacity decay model.
        - **Analytical Solver**: Exact time-to-target evaluation with physical boundary checks.
        - **Dynamic Visualization**: Interactive cooling trajectory with ambient asymptote and target markers.
        """
    )
    st.page_link("pages/2_Heat_Transfer.py", label="Open Heat Transfer Calculator", icon="🔥")

with col3:
    st.markdown("### 🪨 Module C")
    st.markdown("#### Rock & Fluid Dashboard")
    st.markdown(
        """
        - **Petrophysical Analytics**: Core sample data exploration with custom CSV file upload or synthetic benchmark.
        - **Automated Column Heuristics**: Automatic detection of porosity ($\phi$) and permeability ($k$) columns.
        - **Dynamic Cut-Off Filtering**: Real-time sample slicing by minimum reservoir porosity threshold.
        - **Semi-Log Visualizations**: Porosity distribution histograms and semi-log $\phi \text{ vs } k$ crossplots.
        """
    )
    st.page_link("pages/3_Rock_Fluid_Dashboard.py", label="Open Rock & Fluid Dashboard", icon="🪨")

st.markdown("---")

# -----------------------------------------------------------------------------
# System Architecture & Engineering Principles
# -----------------------------------------------------------------------------
st.subheader("📐 System Architecture & Numerical Principles")

st.markdown(
    """
    * **Object-Oriented Design (OOP)**: Domain models (`Fluid`, `Pipe`, `ConductionWall`, `NewtonCoolingSystem`) cleanly encapsulate state, properties, and physical behavior in `engineering.py`.
    * **Root-Solving Robustness**: Implements Brent's method with Haaland explicit initialization for the implicit Colebrook-White friction equation.
    * **Strict Input Validation**: Guard clauses prevent non-physical configurations (e.g., negative diameters, asymptotic temperature crossings, division by zero).
    * **Standard SI Unit System**: All calculations are executed in base SI units ($\text{m}, \text{s}, \text{kg/m}^3, \text{Pa}\cdot\text{s}, \text{W}, \text{K}$) with explicit display conversions.
    """
)

st.markdown("---")
st.caption("Fluid Flow & Heat Transfer Engineering Suite. Built with Streamlit, NumPy, SciPy, Pandas, and Plotly.")
