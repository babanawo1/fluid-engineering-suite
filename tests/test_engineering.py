"""
Automated Pytest Suite for the Fluid Flow & Heat Transfer Engineering Suite.
Verifies analytical calculations, OOP classes, edge cases, and physical boundary exceptions.
"""

import math
import pytest
import numpy as np

from engineering import (
    Fluid,
    Pipe,
    ConductionWall,
    NewtonCoolingSystem,
    friction_factor_haaland,
    friction_factor_colebrook,
    PREDEFINED_FLUIDS,
)


# =============================================================================
# 1. Pipe Flow & Hydraulic Verification Tests
# =============================================================================

def test_fluid_initialization_and_kinematic_viscosity():
    """Verify Fluid properties and kinematic viscosity calculation."""
    water = Fluid(name="Test Water", density=1000.0, dynamic_viscosity=0.001)
    assert water.density == 1000.0
    assert water.dynamic_viscosity == 0.001
    assert math.isclose(water.kinematic_viscosity, 1e-6, rel_tol=1e-5)

    with pytest.raises(ValueError):
        Fluid(name="Invalid Density", density=-500.0, dynamic_viscosity=0.001)

    with pytest.raises(ValueError):
        Fluid(name="Invalid Viscosity", density=1000.0, dynamic_viscosity=-0.001)


def test_pipe_geometry_and_velocity():
    """Verify pipe cross-sectional area and average velocity calculations."""
    pipe = Pipe(diameter=0.1, length=100.0, roughness=0.0001)
    
    # Area = pi * 0.1^2 / 4 = 0.00785398 m^2
    expected_area = math.pi * 0.01 / 4.0
    assert math.isclose(pipe.cross_sectional_area, expected_area, rel_tol=1e-5)

    # Q = 0.00785398 m^3/s -> V = 1.0 m/s
    v = pipe.velocity(flow_rate=expected_area)
    assert math.isclose(v, 1.0, rel_tol=1e-5)

    # Zero flow case
    assert pipe.velocity(0.0) == 0.0

    # Negative flow error
    with pytest.raises(ValueError):
        pipe.velocity(-0.05)


def test_laminar_flow_calculations():
    """
    Test laminar flow:
    D = 0.05 m, L = 50 m
    Fluid: Crude oil (rho = 860 kg/m^3, mu = 0.025 Pa·s)
    Flow rate Q = 0.0005 m^3/s
    A = pi * (0.05)^2 / 4 = 0.0019635 m^2
    V = 0.0005 / 0.0019635 = 0.254648 m/s
    Re = 860 * 0.254648 * 0.05 / 0.025 = 437.995 (Laminar < 2300)
    f = 64 / Re = 64 / 437.995 = 0.14612
    Delta_P = f * (L/D) * (rho * V^2 / 2) = 0.14612 * (50/0.05) * (860 * 0.254648^2 / 2) = 4070.7 Pa
    """
    fluid = Fluid(name="Oil", density=860.0, dynamic_viscosity=0.025)
    pipe = Pipe(diameter=0.05, length=50.0, roughness=0.0)
    flow_rate = 0.0005

    re = pipe.reynolds_number(flow_rate, fluid)
    assert re < 2300.0
    assert pipe.flow_regime(re) == "Laminar"
    assert math.isclose(re, 437.995, rel_tol=1e-3)

    f = pipe.friction_factor(re)
    expected_f = 64.0 / re
    assert math.isclose(f, expected_f, rel_tol=1e-5)

    dp = pipe.pressure_drop(flow_rate, fluid)
    assert math.isclose(dp, 4070.7, rel_tol=1e-2)

    hf = pipe.head_loss(flow_rate, fluid)
    assert math.isclose(hf, dp / (860.0 * 9.81), rel_tol=1e-4)


def test_colebrook_turbulent_friction_solver():
    """
    Test turbulent Colebrook-White root solver against standard Moody chart benchmark:
    Re = 100,000, eps/D = 0.000045 / 0.05 = 0.0009
    Expected f ≈ 0.0219
    """
    re = 100000.0
    eps = 0.000045
    d = 0.05

    f_haaland = friction_factor_haaland(re, eps, d)
    f_colebrook = friction_factor_colebrook(re, eps, d)

    # Haaland is accurate within 1.5% of Colebrook
    assert math.isclose(f_haaland, f_colebrook, rel_tol=0.02)
    assert 0.020 < f_colebrook < 0.024


def test_zero_flow_conditions():
    """Ensure zero flow rate evaluates cleanly without division-by-zero crashes."""
    fluid = PREDEFINED_FLUIDS["Water (20°C)"]
    pipe = Pipe(diameter=0.05, length=100.0, roughness=0.000045)

    assert pipe.velocity(0.0) == 0.0
    assert pipe.reynolds_number(0.0, fluid) == 0.0
    assert pipe.friction_factor(0.0) == 0.0
    assert pipe.pressure_drop(0.0, fluid) == 0.0
    assert pipe.head_loss(0.0, fluid) == 0.0


# =============================================================================
# 2. Heat Transfer Conduction Tests
# =============================================================================

def test_flat_wall_conduction():
    """
    Test 1D Fourier conduction:
    k = 45 W/(m·K), L = 0.15 m, A = 5.0 m^2
    T_hot = 120°C, T_cold = 25°C -> delta_T = 95 K
    R_th = L / (k * A) = 0.15 / (45 * 5.0) = 0.0006667 K/W
    Q_dot = (45 * 5.0 * 95) / 0.15 = 142,500 W (142.5 kW)
    q'' = Q_dot / A = 142,500 / 5.0 = 28,500 W/m^2
    """
    wall = ConductionWall(thermal_conductivity=45.0, thickness=0.15, area=5.0)
    assert math.isclose(wall.thermal_resistance, 0.00066667, rel_tol=1e-4)

    q_dot = wall.heat_rate(t_hot=120.0, t_cold=25.0)
    assert math.isclose(q_dot, 142500.0, rel_tol=1e-4)

    flux = wall.heat_flux(t_hot=120.0, t_cold=25.0)
    assert math.isclose(flux, 28500.0, rel_tol=1e-4)


def test_conduction_invalid_inputs():
    """Test exception raising for non-physical conduction inputs."""
    with pytest.raises(ValueError):
        ConductionWall(thermal_conductivity=-10.0, thickness=0.1, area=1.0)

    with pytest.raises(ValueError):
        ConductionWall(thermal_conductivity=10.0, thickness=-0.1, area=1.0)

    wall = ConductionWall(thermal_conductivity=10.0, thickness=0.1, area=1.0)
    with pytest.raises(ValueError):
        # Hot temperature cooler than cold
        wall.heat_rate(t_hot=20.0, t_cold=50.0)


# =============================================================================
# 3. Newton's Law of Cooling Tests
# =============================================================================

def test_newton_cooling_analytical_solution():
    """
    Test Newton's cooling decay:
    T0 = 95°C, T_inf = 22°C, k_c = 0.015 s^-1
    Target = 45°C
    delta_init = 95 - 22 = 73 K
    delta_target = 45 - 22 = 23 K
    t_target = - (1 / 0.015) * ln(23 / 73) = -66.6667 * (-1.1550) = 77.00 s
    """
    system = NewtonCoolingSystem(t_initial=95.0, t_ambient=22.0, cooling_constant=0.015)
    
    # At t = 0 -> T = 95.0
    assert math.isclose(system.temperature_at_time(0.0), 95.0, rel_tol=1e-5)

    # Time to reach 45°C
    t_calc = system.time_to_temperature(45.0)
    assert math.isclose(t_calc, 77.00, rel_tol=1e-2)

    # Check temperature evaluated at t_calc equals 45.0
    assert math.isclose(system.temperature_at_time(t_calc), 45.0, rel_tol=1e-4)


def test_newton_cooling_boundary_exceptions():
    """Ensure invalid target temperatures raise explicit ValueError."""
    system = NewtonCoolingSystem(t_initial=95.0, t_ambient=22.0, cooling_constant=0.015)

    # Target lower than ambient (impossible in finite time under Newton cooling)
    with pytest.raises(ValueError):
        system.time_to_temperature(20.0)

    # Target equals ambient (infinite asymptotic time)
    with pytest.raises(ValueError):
        system.time_to_temperature(22.0)

    # Target higher than initial in cooling mode
    with pytest.raises(ValueError):
        system.time_to_temperature(100.0)
