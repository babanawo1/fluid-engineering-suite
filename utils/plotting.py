"""
Reusable Plotly visualization helpers for the Fluid Flow & Heat Transfer Engineering Suite.
Standardizes styling, high-contrast engineering grids, SI units, and hover templates.
"""

from typing import List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Consistent Engineering Color Palette
COLOR_PRIMARY = "#1E40AF"     # Deep Blue
COLOR_ACCENT = "#DC2626"      # Coral Red for operating points / targets
COLOR_SECONDARY = "#059669"   # Emerald Green
COLOR_MUTED = "#64748B"       # Slate for grids / borders
BG_PLOT = "#F8FAFC"           # Soft off-white plot background
BG_PAPER = "#FFFFFF"          # Pure white paper


def create_pressure_drop_figure(
    flow_rates: np.ndarray,
    pressure_drops_kpa: np.ndarray,
    current_q: float,
    current_dp_kpa: float,
    fluid_name: str
) -> go.Figure:
    """
    Generate an interactive Plotly figure showing Pressure Drop (kPa) vs Flow Rate (m³/s).
    Highlights the current operating point with an annotated marker.
    """
    fig = go.Figure()

    # Continuous Pressure Drop Curve
    fig.add_trace(go.Scatter(
        x=flow_rates,
        y=pressure_drops_kpa,
        mode="lines",
        name=f"ΔP Curve ({fluid_name})",
        line=dict(color=COLOR_PRIMARY, width=3),
        hovertemplate="<b>Flow Rate (Q):</b> %{x:.4f} m³/s<br><b>Pressure Drop (ΔP):</b> %{y:.2f} kPa<extra></extra>"
    ))

    # Highlight Current Operating Point
    if current_q > 0:
        fig.add_trace(go.Scatter(
            x=[current_q],
            y=[current_dp_kpa],
            mode="markers+text",
            name="Operating Point",
            text=[" Operating Point"],
            textposition="top right",
            marker=dict(color=COLOR_ACCENT, size=12, symbol="diamond"),
            hovertemplate="<b>Operating Point</b><br>Q: %{x:.4f} m³/s<br>ΔP: %{y:.2f} kPa<extra></extra>"
        ))

    fig.update_layout(
        title=dict(text="<b>Frictional Pressure Drop vs. Volumetric Flow Rate</b>", font=dict(size=18, color="#0F172A")),
        xaxis=dict(
            title="<b>Volumetric Flow Rate, Q (m³/s)</b>",
            gridcolor="#E2E8F0",
            zeroline=True,
            zerolinecolor="#94A3B8"
        ),
        yaxis=dict(
            title="<b>Pressure Drop, ΔP (kPa)</b>",
            gridcolor="#E2E8F0",
            zeroline=True,
            zerolinecolor="#94A3B8"
        ),
        plot_bgcolor=BG_PLOT,
        paper_bgcolor=BG_PAPER,
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=40, t=70, b=50)
    )

    return fig


def create_cooling_curve_figure(
    times: np.ndarray,
    temperatures: np.ndarray,
    t_initial: float,
    t_ambient: float,
    t_target: float,
    time_target: float
) -> go.Figure:
    """
    Generate an interactive Plotly figure for Newton's Law of Cooling.
    Includes ambient asymptote, initial state, and target operating state.
    """
    fig = go.Figure()

    # Asymptotic Ambient Temperature Line
    fig.add_trace(go.Scatter(
        x=[0, times[-1]],
        y=[t_ambient, t_ambient],
        mode="lines",
        name=f"Ambient Temp T_inf ({t_ambient:.1f}°C)",
        line=dict(color="#64748B", width=2, dash="dash"),
        hoverinfo="skip"
    ))

    # Continuous Cooling Temperature Curve
    fig.add_trace(go.Scatter(
        x=times,
        y=temperatures,
        mode="lines",
        name="Temperature T(t)",
        line=dict(color=COLOR_PRIMARY, width=3),
        hovertemplate="<b>Time:</b> %{x:.1f} s<br><b>Temperature:</b> %{y:.2f} °C<extra></extra>"
    ))

    # Target Temperature Point
    fig.add_trace(go.Scatter(
        x=[time_target],
        y=[t_target],
        mode="markers+text",
        name=f"Target ({t_target:.1f}°C @ {time_target:.1f}s)",
        text=[f" Target ({time_target:.1f}s)"],
        textposition="top right",
        marker=dict(color=COLOR_ACCENT, size=11, symbol="star"),
        hovertemplate="<b>Target Point</b><br>Time: %{x:.2f} s<br>Temp: %{y:.2f} °C<extra></extra>"
    ))

    # Initial Temperature Point
    fig.add_trace(go.Scatter(
        x=[0],
        y=[t_initial],
        mode="markers",
        name=f"Initial T0 ({t_initial:.1f}°C)",
        marker=dict(color=COLOR_SECONDARY, size=10, symbol="circle"),
        hovertemplate="<b>Initial Temp:</b> %{y:.2f} °C at t=0<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text="<b>Transient Cooling Curve (Newton's Law of Cooling)</b>", font=dict(size=18, color="#0F172A")),
        xaxis=dict(
            title="<b>Time, t (seconds)</b>",
            gridcolor="#E2E8F0",
            zeroline=True
        ),
        yaxis=dict(
            title="<b>Temperature, T (°C)</b>",
            gridcolor="#E2E8F0",
            zeroline=False
        ),
        plot_bgcolor=BG_PLOT,
        paper_bgcolor=BG_PAPER,
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=40, t=70, b=50)
    )

    return fig


def create_porosity_histogram(df: pd.DataFrame, poro_col: str) -> go.Figure:
    """
    Generate an interactive histogram of rock porosity distribution.
    """
    fig = px.histogram(
        df,
        x=poro_col,
        nbins=20,
        title="<b>Porosity Distribution Histogram</b>",
        labels={poro_col: "Porosity (%)"},
        color_discrete_sequence=[COLOR_PRIMARY],
        opacity=0.85
    )

    fig.update_layout(
        xaxis=dict(title="<b>Porosity (%)</b>", gridcolor="#E2E8F0"),
        yaxis=dict(title="<b>Number of Core Samples (Frequency)</b>", gridcolor="#E2E8F0"),
        plot_bgcolor=BG_PLOT,
        paper_bgcolor=BG_PAPER,
        margin=dict(l=60, r=40, t=70, b=50),
        bargap=0.08
    )

    return fig


def create_poro_perm_crossplot(df: pd.DataFrame, poro_col: str, perm_col: str) -> go.Figure:
    """
    Generate a semi-log Porosity vs Permeability crossplot for reservoir characterization.
    """
    valid_df = df[df[perm_col] > 0].copy()

    fig = px.scatter(
        valid_df,
        x=poro_col,
        y=perm_col,
        title="<b>Porosity vs. Permeability Crossplot (Semi-Log Scale)</b>",
        labels={
            poro_col: "Porosity (%)",
            perm_col: "Permeability (mD, Log Scale)"
        },
        color_discrete_sequence=[COLOR_PRIMARY],
        hover_data=valid_df.columns.tolist()
    )

    fig.update_traces(marker=dict(size=9, opacity=0.8, line=dict(width=1, color="#0F172A")))

    fig.update_layout(
        xaxis=dict(title="<b>Porosity, φ (%)</b>", gridcolor="#E2E8F0"),
        yaxis=dict(
            title="<b>Permeability, k (mD) — Log10 Scale</b>",
            type="log",
            gridcolor="#E2E8F0",
            dtick=1
        ),
        plot_bgcolor=BG_PLOT,
        paper_bgcolor=BG_PAPER,
        margin=dict(l=60, r=40, t=70, b=50)
    )

    return fig
