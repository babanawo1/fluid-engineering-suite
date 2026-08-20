# Fluid Flow & Thermal Systems Engineering Computing Suite

An interactive, multi-module computational engineering platform for fluid mechanics, thermal transport, and reservoir petrophysics. Built with an Object-Oriented Architecture (OOP) in Python (`Streamlit`, `NumPy`, `SciPy`, `Pandas`, `Plotly`) and companion TypeScript engineering utilities.

---

## 🌟 Executive Summary & Key Modules

| Module | Core Physical Principles | Key Features & Visualizations |
| :--- | :--- | :--- |
| **Module A: Pipe Flow Analyser** | Darcy-Weisbach & Colebrook-White implicit friction equation | Interactive $\Delta P \text{ vs. } Q$ curves, laminar/transitional/turbulent flow detection, Colebrook root-solver via Brent's method with Haaland initialization, CSV hydraulic profile export. |
| **Module B: Heat Transfer Calculator** | 1D Fourier steady conduction & Lumped Capacitance (Newton's cooling) | Multi-layer temperature profile cross-sections, transient cooling curves ($T(t) \text{ vs. } t$) with analytical time-to-target resolution and logarithmic asymptotic guards. |
| **Module C: Rock & Fluid Dashboard** | Petrophysical core evaluation & Kozeny-Carman permeability | 40-sample core plug dataset analysis, dynamic porosity cut-off filtering, summary statistical tables, semi-log $\phi \text{ vs. } k$ crossplots, filtered data export. |
| **Module D: Code Quality & Testing** | Automated testing, OOP design, and deployment | Full `pytest` unit test suite, strict input validation, comprehensive verification benchmarks, and Streamlit Cloud configuration. |

---

## 🚀 Live Demonstration & Deployment

* **Live Streamlit Web Application**: [Deploy via Streamlit Community Cloud](https://share.streamlit.io/)
* **Repository**: `https://github.com/<your-username>/fluid-engineering-suite`
* **Entry Point**: `app.py`

---

## ⚙️ Architecture & Numerical Methods

### 1. Robust Colebrook-White Root Solving
The implicit Colebrook-White formulation for turbulent friction factor ($f$):
$$\frac{1}{\sqrt{f}} = -2 \log_{10}\left( \frac{\epsilon / D}{3.7} + \frac{2.51}{\text{Re} \sqrt{f}} \right)$$

To guarantee convergence across arbitrary Reynolds numbers ($\text{Re} \ge 4000$) and relative roughness values ($\epsilon/D \in [0, 0.05]$), the solver utilizes **Brent's method** bounded in $[0.005, 0.15]$, seeded with an explicit **Haaland initial estimate**:
$$f_0 = \left[ -1.8 \log_{10}\left( \left(\frac{\epsilon/D}{3.7}\right)^{1.11} + \frac{6.9}{\text{Re}} \right) \right]^{-2}$$

### 2. Transient Thermal System Validation
Newton's Law of Cooling is governed by the characteristic time constant $\tau = \frac{\rho V c_p}{h A_s}$:
$$T(t) = T_\infty + (T_0 - T_\infty) e^{-t / \tau}$$
$$t_{\text{target}} = -\tau \ln\left( \frac{T_{\text{target}} - T_\infty}{T_0 - T_\infty} \right)$$
*Built-in guards reject unphysical conditions where $T_{\text{target}}$ lies outside the open interval between $T_0$ and $T_\infty$.*

---

## 💻 Local Setup & Execution

### Prerequisites
* Python 3.9+ 
* `pip` package manager

### 1. Clone & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/<your-username>/fluid-engineering-suite.git
cd fluid-engineering-suite

# Install required Python packages
pip install -r requirements.txt
