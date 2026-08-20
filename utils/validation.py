"""
Validation utility functions for the Fluid Flow & Heat Transfer Engineering Suite.
Ensures strict physical bounds checking, safe numeric parsing, and clean error reporting.
"""

from typing import Tuple, Optional, Dict, Any, List
import pandas as pd


def validate_positive_number(val: Any, param_name: str, allow_zero: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate that a given numeric input is non-negative or strictly positive.

    Args:
        val: The input value to check.
        param_name: Human-readable name of the parameter.
        allow_zero: Whether 0 is considered valid.

    Returns:
        Tuple of (is_valid, error_message).
    """
    try:
        num = float(val)
    except (ValueError, TypeError):
        return False, f"{param_name} must be a valid numeric value."

    if allow_zero:
        if num < 0:
            return False, f"{param_name} must be greater than or equal to 0. Received: {num}"
    else:
        if num <= 0:
            return False, f"{param_name} must be strictly greater than 0. Received: {num}"

    return True, None


def validate_pipe_inputs(
    diameter: float,
    length: float,
    roughness: float,
    flow_rate: float,
    density: float,
    viscosity: float
) -> Tuple[bool, List[str]]:
    """
    Comprehensive validation for pipe flow inputs.

    Returns:
        Tuple of (is_valid, list_of_error_messages).
    """
    errors: List[str] = []

    valid, err = validate_positive_number(diameter, "Internal Pipe Diameter (D)", allow_zero=False)
    if not valid: errors.append(err)

    valid, err = validate_positive_number(length, "Pipe Length (L)", allow_zero=False)
    if not valid: errors.append(err)

    valid, err = validate_positive_number(roughness, "Pipe Absolute Roughness (ε)", allow_zero=True)
    if not valid: errors.append(err)

    valid, err = validate_positive_number(flow_rate, "Volumetric Flow Rate (Q)", allow_zero=True)
    if not valid: errors.append(err)

    valid, err = validate_positive_number(density, "Fluid Density (ρ)", allow_zero=False)
    if not valid: errors.append(err)

    valid, err = validate_positive_number(viscosity, "Dynamic Viscosity (μ)", allow_zero=False)
    if not valid: errors.append(err)

    if diameter > 0 and roughness > diameter:
        errors.append(f"Absolute roughness ({roughness} m) cannot exceed pipe diameter ({diameter} m).")

    return len(errors) == 0, errors


def validate_conduction_inputs(
    thermal_conductivity: float,
    thickness: float,
    area: float,
    t_hot: float,
    t_cold: float
) -> Tuple[bool, List[str]]:
    """
    Validate 1D Fourier conduction wall parameters.
    """
    errors: List[str] = []

    valid, err = validate_positive_number(thermal_conductivity, "Thermal Conductivity (k)", allow_zero=False)
    if not valid: errors.append(err)

    valid, err = validate_positive_number(thickness, "Wall Thickness (L)", allow_zero=False)
    if not valid: errors.append(err)

    valid, err = validate_positive_number(area, "Wall Surface Area (A)", allow_zero=False)
    if not valid: errors.append(err)

    try:
        t_h = float(t_hot)
        t_c = float(t_cold)
        if t_h < t_c:
            errors.append(f"Hot-side temperature ({t_h}°C) cannot be colder than cold-side temperature ({t_c}°C).")
    except (ValueError, TypeError):
        errors.append("Temperatures must be valid numerical values.")

    return len(errors) == 0, errors


def validate_cooling_inputs(
    t_initial: float,
    t_ambient: float,
    t_target: float,
    cooling_constant: float
) -> Tuple[bool, List[str]]:
    """
    Validate Newton's cooling parameters and ensure the analytical logarithm argument remains within physical bounds.
    """
    errors: List[str] = []

    valid, err = validate_positive_number(cooling_constant, "Cooling Constant (k_c)", allow_zero=False)
    if not valid: errors.append(err)

    try:
        t0 = float(t_initial)
        t_inf = float(t_ambient)
        t_tgt = float(t_target)

        if t0 == t_inf:
            errors.append("Initial temperature equals ambient temperature (system already in thermal equilibrium).")
        elif t0 > t_inf:
            # Cooling regime
            if t_tgt >= t0:
                errors.append(f"For cooling (T0 > T_ambient), target temperature ({t_tgt}°C) must be lower than initial temperature ({t0}°C).")
            if t_tgt <= t_inf:
                errors.append(f"Target temperature ({t_tgt}°C) cannot reach or cross ambient temperature ({t_inf}°C) in finite time.")
        else:
            # Heating regime
            if t_tgt <= t0:
                errors.append(f"For heating (T0 < T_ambient), target temperature ({t_tgt}°C) must be higher than initial temperature ({t0}°C).")
            if t_tgt >= t_inf:
                errors.append(f"Target temperature ({t_tgt}°C) cannot reach or exceed ambient temperature ({t_inf}°C) in finite time.")

    except (ValueError, TypeError):
        errors.append("Temperatures must be valid numerical values.")

    return len(errors) == 0, errors


def validate_csv_dataset(df: pd.DataFrame) -> Tuple[bool, Optional[str], Dict[str, str]]:
    """
    Inspect an uploaded DataFrame for rock and fluid analysis.
    Identifies porosity and permeability columns based on standard naming heuristics.

    Returns:
        Tuple of (is_valid, error_msg, detected_columns_dict).
    """
    if df.empty:
        return False, "The uploaded CSV file contains no data rows.", {}

    if len(df.columns) == 0:
        return False, "No columns were found in the uploaded file.", {}

    detected_cols: Dict[str, str] = {}

    # Heuristic detection for porosity column
    porosity_candidates = ["porosity", "porosity_percent", "porosity_%", "phi", "poro", "por", "phi_%"]
    for col in df.columns:
        norm = col.strip().lower().replace(" ", "_")
        if norm in porosity_candidates or "poros" in norm or "phi" in norm:
            detected_cols["porosity"] = col
            break

    # Heuristic detection for permeability column
    perm_candidates = ["permeability", "permeability_md", "perm", "k_md", "k", "perm_md"]
    for col in df.columns:
        norm = col.strip().lower().replace(" ", "_")
        if norm in perm_candidates or "perm" in norm or norm.startswith("k_"):
            detected_cols["permeability"] = col
            break

    # Check that at least numeric columns exist
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if len(numeric_cols) == 0:
        return False, "No numeric data columns were detected in the uploaded CSV file.", {}

    return True, None, detected_cols
