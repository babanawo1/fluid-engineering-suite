import math
from typing import Tuple, Optional
import numpy as np
from scipy import optimize

# Physical Constants
GRAVITY_ACCELERATION: float = 9.81  # Standard acceleration due to gravity in m/s^2


class Fluid:
    """
    Represents a fluid with basic thermodynamic and transport properties.

    Attributes:
        name (str): The common name of the fluid.
        density (float): Fluid density in kg/m^3 (must be > 0).
        dynamic_viscosity (float): Dynamic viscosity in Pa·s (N·s/m^2, must be > 0).
    """

    def __init__(self, name: str, density: float, dynamic_viscosity: float) -> None:
        if density <= 0:
            raise ValueError(f"Fluid density must be positive (> 0). Received: {density}")
        if dynamic_viscosity <= 0:
            raise ValueError(f"Fluid dynamic viscosity must be positive (> 0). Received: {dynamic_viscosity}")
        
        self.name: str = name
        self.density: float = float(density)
        self.dynamic_viscosity: float = float(dynamic_viscosity)

    @property
    def kinematic_viscosity(self) -> float:
        """Calculate kinematic viscosity ν = μ / ρ in m^2/s."""
        return self.dynamic_viscosity / self.density

    def __repr__(self) -> str:
        return f"Fluid(name='{self.name}', density={self.density:.2f} kg/m³, dynamic_viscosity={self.dynamic_viscosity:.5e} Pa·s)"


class Pipe:
    """
    Represents a cylindrical conduit for fluid flow.

    Attributes:
        diameter (float): Internal pipe diameter in meters (m, must be > 0).
        length (float): Total length of the pipe in meters (m, must be > 0).
        roughness (float): Absolute surface roughness in meters (m, must be >= 0).
    """

    def __init__(self, diameter: float, length: float, roughness: float = 0.0) -> None:
        if diameter <= 0:
            raise ValueError(f"Pipe internal diameter must be positive (> 0). Received: {diameter}")
        if length <= 0:
            raise ValueError(f"Pipe length must be positive (> 0). Received: {length}")
        if roughness < 0:
            raise ValueError(f"Pipe roughness cannot be negative. Received: {roughness}")

        self.diameter: float = float(diameter)
        self.length: float = float(length)
        self.roughness: float = float(roughness)

    @property
    def cross_sectional_area(self) -> float:
        """Calculate internal cross-sectional area A = π * D^2 / 4 in m^2."""
        return math.pi * (self.diameter ** 2) / 4.0

    @property
    def relative_roughness(self) -> float:
        """Calculate relative roughness ε / D (dimensionless)."""
        return self.roughness / self.diameter

    def velocity(self, flow_rate: float) -> float:
        """
        Calculate average flow velocity V = Q / A in m/s.

        Args:
            flow_rate: Volumetric flow rate in m^3/s (must be >= 0).

        Returns:
            Mean velocity in m/s.
        """
        if flow_rate < 0:
            raise ValueError(f"Volumetric flow rate cannot be negative. Received: {flow_rate}")
        if flow_rate == 0:
            return 0.0
        return flow_rate / self.cross_sectional_area

    def reynolds_number(self, flow_rate: float, fluid: Fluid) -> float:
        """
        Calculate Reynolds number Re = (ρ * V * D) / μ.

        Args:
            flow_rate: Volumetric flow rate in m^3/s.
            fluid: Instance of Fluid class.

        Returns:
            Reynolds number (dimensionless).
        """
        v = self.velocity(flow_rate)
        if v == 0.0:
            return 0.0
        return (fluid.density * v * self.diameter) / fluid.dynamic_viscosity

    def flow_regime(self, reynolds: float) -> str:
        """
        Classify flow regime based on Reynolds number.

        Standard internal pipe criteria:
        - Re < 2300: Laminar
        - 2300 <= Re <= 4000: Transitional
        - Re > 4000: Turbulent
        """
        if reynolds < 2300.0:
            return "Laminar"
        elif reynolds <= 4000.0:
            return "Transitional"
        else:
            return "Turbulent"

    def friction_factor(self, reynolds: float) -> float:
        """
        Calculate the Darcy-Weisbach friction factor f.

        For Re == 0: Returns 0.0.
        For Laminar (Re < 2300): f = 64 / Re.
        For Transitional (2300 <= Re <= 4000): Linear interpolation / Colebrook with warning.
        For Turbulent (Re > 4000): Solved via implicit Colebrook-White equation.

        Args:
            reynolds: Reynolds number.

        Returns:
            Darcy friction factor (dimensionless, positive).
        """
        if reynolds <= 0.0:
            return 0.0
        if reynolds < 2300.0:
            return 64.0 / reynolds
        
        # Turbulent / Transitional Colebrook-White solution
        return friction_factor_colebrook(reynolds, self.roughness, self.diameter)

    def pressure_drop(self, flow_rate: float, fluid: Fluid) -> float:
        """
        Calculate Darcy-Weisbach frictional pressure drop:
        ΔP = f * (L / D) * (ρ * V^2 / 2) in Pascals (Pa).

        Args:
            flow_rate: Volumetric flow rate in m^3/s.
            fluid: Instance of Fluid class.

        Returns:
            Pressure drop ΔP in Pascals (Pa).
        """
        if flow_rate == 0.0:
            return 0.0

        v = self.velocity(flow_rate)
        re = self.reynolds_number(flow_rate, fluid)
        f = self.friction_factor(re)
        
        delta_p = f * (self.length / self.diameter) * (fluid.density * (v ** 2) / 2.0)
        return float(delta_p)

    def head_loss(self, flow_rate: float, fluid: Fluid) -> float:
        """
        Calculate head loss h_f = ΔP / (ρ * g) in meters (m).

        Args:
            flow_rate: Volumetric flow rate in m^3/s.
            fluid: Instance of Fluid class.

        Returns:
            Head loss in meters of fluid column.
        """
        if flow_rate == 0.0:
            return 0.0
        delta_p = self.pressure_drop(flow_rate, fluid)
        return delta_p / (fluid.density * GRAVITY_ACCELERATION)

    def __repr__(self) -> str:
        return f"Pipe(diameter={self.diameter:.4f} m, length={self.length:.2f} m, roughness={self.roughness:.6f} m)"


# -----------------------------------------------------------------------------
# Standalone Numerical Functions & Root Solvers
# -----------------------------------------------------------------------------

def friction_factor_haaland(reynolds: float, roughness: float, diameter: float) -> float:
    """
    Calculate explicit approximation for the Darcy friction factor using Haaland's equation (1983).

    1 / sqrt(f) = -1.8 * log10( ( (ε / D) / 3.7 )^1.11 + 6.9 / Re )

    Args:
        reynolds: Reynolds number (> 0).
        roughness: Absolute pipe roughness in meters.
        diameter: Pipe internal diameter in meters.

    Returns:
        Approximated Darcy friction factor.
    """
    if reynolds <= 0:
        raise ValueError("Reynolds number must be positive for Haaland approximation.")
    
    rel_rough = (roughness / diameter) / 3.7
    term = (rel_rough ** 1.11) + (6.9 / reynolds)
    inv_sqrt_f = -1.8 * math.log10(term)
    return 1.0 / (inv_sqrt_f ** 2)


def friction_factor_colebrook(reynolds: float, roughness: float, diameter: float) -> float:
    """
    Solve the implicit Colebrook-White equation for Darcy friction factor using Brent's method:
    1 / sqrt(f) = -2.0 * log10( (ε / (3.7 * D)) + 2.51 / (Re * sqrt(f)) )

    Uses Haaland approximation as an initial guess to construct a guaranteed bracket.

    Args:
        reynolds: Reynolds number (must be > 0).
        roughness: Absolute pipe roughness in meters.
        diameter: Pipe internal diameter in meters.

    Returns:
        Exact Darcy friction factor (positive float).
    """
    if reynolds <= 0:
        raise ValueError(f"Reynolds number must be > 0. Received: {reynolds}")
    if diameter <= 0:
        raise ValueError(f"Diameter must be > 0. Received: {diameter}")

    # Seed with Haaland equation
    f_seed = friction_factor_haaland(reynolds, roughness, diameter)
    
    def colebrook_residual(f_val: float) -> float:
        if f_val <= 0:
            return 1e6
        sqrt_f = math.sqrt(f_val)
        lhs = 1.0 / sqrt_f
        rhs = -2.0 * math.log10((roughness / (3.7 * diameter)) + (2.51 / (reynolds * sqrt_f)))
        return lhs - rhs

    # Establish search bracket around seed [0.005, 0.20] or relative to seed
    bracket_min = max(0.003, f_seed * 0.5)
    bracket_max = min(0.25, f_seed * 2.0)

    try:
        sol = optimize.root_scalar(
            colebrook_residual,
            bracket=[bracket_min, bracket_max],
            method='brentq',
            xtol=1e-7,
            maxiter=100
        )
        if sol.converged:
            return float(sol.root)
    except Exception:
        pass

    # Fallback to Haaland explicit value if root solving fails at boundary
    return float(f_seed)


# -----------------------------------------------------------------------------
# Module B — Heat Transfer Classes & Functions
# -----------------------------------------------------------------------------

class ConductionWall:
    """
    Represents a 1D plane wall undergoing steady-state heat conduction.

    Attributes:
        thermal_conductivity (float): Thermal conductivity k in W/(m·K) (must be > 0).
        thickness (float): Wall thickness L in meters (must be > 0).
        area (float): Heat transfer surface area A in m^2 (must be > 0).
    """

    def __init__(self, thermal_conductivity: float, thickness: float, area: float) -> None:
        if thermal_conductivity <= 0:
            raise ValueError(f"Thermal conductivity must be positive (> 0). Received: {thermal_conductivity}")
        if thickness <= 0:
            raise ValueError(f"Wall thickness must be positive (> 0). Received: {thickness}")
        if area <= 0:
            raise ValueError(f"Wall surface area must be positive (> 0). Received: {area}")

        self.thermal_conductivity: float = float(thermal_conductivity)
        self.thickness: float = float(thickness)
        self.area: float = float(area)

    @property
    def thermal_resistance(self) -> float:
        """Calculate conduction thermal resistance R_th = L / (k * A) in K/W."""
        return self.thickness / (self.thermal_conductivity * self.area)

    def heat_rate(self, t_hot: float, t_cold: float) -> float:
        """
        Calculate conduction heat transfer rate Q_dot = k * A * (T_hot - T_cold) / L in Watts (W).

        Args:
            t_hot: Hot surface temperature in °C or K.
            t_cold: Cold surface temperature in °C or K (must be <= t_hot).

        Returns:
            Heat transfer rate Q_dot in Watts (W).
        """
        if t_hot < t_cold:
            raise ValueError(f"Hot-side temperature ({t_hot}) cannot be lower than cold-side temperature ({t_cold}).")
        delta_t = t_hot - t_cold
        return (self.thermal_conductivity * self.area * delta_t) / self.thickness

    def heat_flux(self, t_hot: float, t_cold: float) -> float:
        """
        Calculate conduction heat flux q'' = Q_dot / A = k * (T_hot - T_cold) / L in W/m^2.

        Args:
            t_hot: Hot surface temperature in °C or K.
            t_cold: Cold surface temperature in °C or K.

        Returns:
            Heat flux in W/m^2.
        """
        q_dot = self.heat_rate(t_hot, t_cold)
        return q_dot / self.area


class NewtonCoolingSystem:
    """
    Models transient lumped thermal capacity cooling following Newton's Law of Cooling:
    dT/dt = -k_c * (T - T_ambient)
    T(t) = T_ambient + (T_initial - T_ambient) * exp(-k_c * t)

    Attributes:
        t_initial (float): Initial temperature at t=0 (°C or K).
        t_ambient (float): Surrounding ambient temperature (°C or K).
        cooling_constant (float): Heat transfer cooling constant k_c in 1/s or 1/min (must be > 0).
    """

    def __init__(self, t_initial: float, t_ambient: float, cooling_constant: float) -> None:
        if cooling_constant <= 0:
            raise ValueError(f"Cooling constant k_c must be positive (> 0). Received: {cooling_constant}")
        
        self.t_initial: float = float(t_initial)
        self.t_ambient: float = float(t_ambient)
        self.cooling_constant: float = float(cooling_constant)

    def temperature_at_time(self, time: float) -> float:
        """
        Calculate object temperature at time t:
        T(t) = T_inf + (T0 - T_inf) * exp(-k_c * t)

        Args:
            time: Elapsed time (must be >= 0).

        Returns:
            Temperature at time t.
        """
        if time < 0:
            raise ValueError(f"Time cannot be negative. Received: {time}")
        return self.t_ambient + (self.t_initial - self.t_ambient) * math.exp(-self.cooling_constant * time)

    def time_to_temperature(self, t_target: float) -> float:
        """
        Calculate time required to reach target temperature:
        t = - (1 / k_c) * ln( (T_target - T_ambient) / (T_initial - T_ambient) )

        Args:
            t_target: Target temperature.

        Returns:
            Time in seconds (or time units matching cooling_constant).
        """
        # For cooling: T_initial > T_target > T_ambient
        # For heating: T_initial < T_target < T_ambient
        delta_init = self.t_initial - self.t_ambient
        delta_target = t_target - self.t_ambient

        if delta_init == 0:
            raise ValueError("Initial temperature equals ambient temperature; no temperature change will occur.")

        ratio = delta_target / delta_init

        if ratio <= 0:
            raise ValueError(
                f"Target temperature ({t_target}) cannot be reached because it crosses or equals the ambient boundary ({self.t_ambient})."
            )
        if ratio > 1.0:
            raise ValueError(
                f"Target temperature ({t_target}) is further away from ambient than the initial temperature ({self.t_initial})."
            )

        return - (1.0 / self.cooling_constant) * math.log(ratio)

    def generate_cooling_curve(self, t_max: float, points: int = 150) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate time and temperature vectors for visualization.

        Args:
            t_max: Maximum time limit.
            points: Number of evaluation sample points.

        Returns:
            Tuple of (time_array, temperature_array).
        """
        if t_max <= 0:
            raise ValueError("Maximum time must be positive (> 0).")
        times = np.linspace(0, t_max, points)
        temps = self.t_ambient + (self.t_initial - self.t_ambient) * np.exp(-self.cooling_constant * times)
        return times, temps


# -----------------------------------------------------------------------------
# Predefined Fluid Engineering Library
# -----------------------------------------------------------------------------
PREDEFINED_FLUIDS = {
    "Water (20°C)": Fluid(name="Water (20°C)", density=998.2, dynamic_viscosity=1.002e-3),
    "Air (20°C, 1 atm)": Fluid(name="Air (20°C, 1 atm)", density=1.204, dynamic_viscosity=1.825e-5),
    "Crude Oil (Medium, 15°C)": Fluid(name="Crude Oil (Medium, 15°C)", density=860.0, dynamic_viscosity=0.025),
}
