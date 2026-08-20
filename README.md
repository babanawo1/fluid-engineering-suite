# Fluid Flow & Heat Transfer Engineering Suite

An interactive engineering computing application developed with Python and Streamlit.

The application combines computational engineering calculations, object-oriented programming, data analysis, visualization, and interactive user interfaces.

## Live Application

[Launch the Fluid Flow & Heat Transfer Engineering Suite](https://fluid-engineering-suite.streamlit.app/)

## GitHub Repository

https://github.com/babanawo1/fluid-engineering-suite

## Modules

### Module A — Pipe Flow Analyser

- Fluid property selection
- Pipe geometry and flow-rate inputs
- Velocity calculation
- Reynolds number
- Flow regime identification
- Darcy friction factor
- Pressure-drop calculation
- Pressure-drop versus flow-rate visualization
- CSV export

### Module B — Heat Transfer Calculator

- Steady-state conduction through a flat wall
- Newton's Law of Cooling
- Cooling-time calculation
- Interactive temperature-versus-time cooling curve
- Physical descriptions and unit guidance

### Module C — Rock & Fluid Data Dashboard

- User CSV file upload
- Summary statistics
- Porosity filtering
- Porosity histogram
- Porosity-permeability crossplot
- Filtered CSV export

## Technologies

- Python
- Streamlit
- Pandas
- NumPy
- Matplotlib
- Object-Oriented Programming
- CSV data processing

## Project Structure

```text
fluid-engineering-suite/
├── app.py
├── engineering.py
├── requirements.txt
├── pages/
│   ├── 1_Pipe_Flow_Analyser.py
│   ├── 2_Heat_Transfer.py
│   └── 3_Rock_Fluid_Dashboard.py
├── data/
├── utils/
├── tests/
└── docs/
