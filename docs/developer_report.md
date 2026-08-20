# Fluid Flow & Heat Transfer Engineering Suite — Technical Report

**Author:** [YOUR_NAME]  
**Course/Module:** Engineering Computing & Numerical Methods  
**Date:** 2026-08-19  

---

## 1. Interesting Engineering Insight: Nonlinear Hydraulic Losses in Conduit Flow

An engineering insight highlighted by this suite is the strong **nonlinear escalation of frictional pressure drop** with increasing volumetric flow rate ($Q$). 

In laminar internal flow ($Re < 2300$), the friction factor is inversely proportional to velocity ($f = 64/Re$), causing pressure drop to scale linearly with velocity:
$$\Delta P_{\text{laminar}} = \frac{32 \mu L V}{D^2} \propto Q$$

However, once the transition to turbulent flow occurs ($Re > 4000$), the friction factor becomes governed by the Colebrook-White equation and approaches a nearly constant value at high Reynolds numbers (the complete turbulence regime). Consequently, the Darcy-Weisbach equation reveals a quadratic dependence on velocity:
$$\Delta P_{\text{turbulent}} = f \frac{L}{D} \frac{\rho V^2}{2} \propto Q^2$$

This quadratic relationship means that doubling the throughput of a piping system increases frictional pressure drop by approximately **four-fold**, which directly increases required pumping power by a factor of eight ($P_{\text{pump}} = \Delta P \cdot Q \propto Q^3$). The interactive performance curves generated in Module A clearly demonstrate this phenomenon, assisting engineers in identifying the optimal economic pipe diameter where capital expenditure balances lifecycle operational pumping energy.

---

## 2. Technical Challenge & Implementation: Solving the Implicit Colebrook-White Equation

The primary numerical challenge in this project was solving the implicit Colebrook-White equation for turbulent Darcy friction factors:
$$\frac{1}{\sqrt{f}} = -2 \log_{10}\left( \frac{\varepsilon}{3.7 D} + \frac{2.51}{Re \sqrt{f}} \right)$$

Because $f$ is present on both sides inside square roots and logarithms, no closed-form analytical solution exists. 

To ensure numerical stability across 8 orders of magnitude of Reynolds numbers ($4 \times 10^3 \le Re \le 10^8$) and relative roughness values ($0 \le \varepsilon/D \le 0.05$):
1. **Explicit Seeding**: The explicit **Haaland equation (1983)** was implemented to provide an accurate initial estimate ($f_{\text{seed}}$ within 1.5% of the exact root).
2. **Bracketed Root-Finding**: Using `scipy.optimize.root_scalar` with Brent's method (`brentq`), a guaranteed bounded bracket $[0.5 f_{\text{seed}}, 2.0 f_{\text{seed}}]$ was constructed, ensuring sub-millisecond convergence with zero divergence risk.
3. **Physical Boundary Guards**: Safe handling of $Q=0$ and strict laminar branching ($f = 64/Re$) prevent numerical division-by-zero singularities.

---

## 3. Future Engineering Improvements

1. **Non-Newtonian Fluid Rheology**: Expand the fluid mechanics engine to support power-law (Ostwald-de Waele) and Bingham plastic fluids, enabling drilling mud and polymer slurry hydraulics.
2. **Transient Pipe Water Hammer (Method of Characteristics)**: Implement 1D hyperbolic wave equation solvers to model acoustic pressure surge waves during rapid valve closures.
3. **Multi-Layer Composite Wall Conduction**: Extend the thermal module to solve composite cylindrical and spherical wall series resistances with convective boundary layers ($U$-value analysis).
