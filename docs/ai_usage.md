# AI Usage & Responsible Development Log

This document records representative AI prompts utilized during the design and software engineering lifecycle of the **Fluid Flow & Heat Transfer Engineering Suite**, along with the manual engineering verification, corrections applied, and technical lessons learned.

---

## Prompt Log 1: Colebrook-White Friction Factor Numerical Solver

* **Prompt:**
  > "How can I implement an implicit root-solver in Python for the Colebrook-White friction factor equation in pipe flow without running into convergence instability or dividing by zero?"
* **Purpose:**
  > To identify a fast and numerically robust method for solving the transcendental Colebrook-White equation across both smooth and rough turbulent flow regimes.
* **AI Output:**
  > Suggested using `scipy.optimize.root_scalar` with Brent's method and seeding it with the explicit Haaland approximation to ensure bracket convergence.
* **Independent Verification:**
  > Cross-checked the friction factors generated against standard textbook Moody chart data points ($Re = 10^4, 10^5, 10^6$ at $\varepsilon/D = 0.001$). Confirmed convergence within 4 iterations.
* **Correction Applied:**
  > Added safety guards for $Re \le 0$ and laminar flow conditions ($Re < 2300$) so the solver is not called unnecessarily when the analytical relation $f = 64/Re$ applies.
* **Lesson Learned:**
  > Implicit nonlinear equations in engineering fluid mechanics must always be paired with physical domain checks before invoking iterative solvers.

---

## Prompt Log 2: Logarithmic Argument Protection for Newton's Law of Cooling

* **Prompt:**
  > "What edge cases exist when solving for time in Newton's Law of Cooling analytically using $t = -1/k_c \ln((T_{\text{target}} - T_{\infty}) / (T_0 - T_{\infty}))$?"
* **Purpose:**
  > To ensure the analytical cooling calculator never crashes on non-physical user input.
* **AI Output:**
  > Highlighted that when $T_{\text{target}} \le T_{\infty}$ during cooling ($T_0 > T_{\infty}$), the argument of the logarithm becomes non-positive ($\le 0$), causing a math domain error.
* **Independent Verification:**
  > Evaluated the physical limits of lumped thermal capacity: an object cools towards ambient temperature asymptotically and can only reach ambient in the limit as $t \to \infty$.
* **Correction Applied:**
  > Implemented pre-flight guard clauses in `utils/validation.py` and `engineering.py` that raise clean descriptive error messages before any logarithm operation is evaluated.
* **Lesson Learned:**
  > Software safety in engineering requires translating physical thermodynamic constraints into software boundary validations.

---

## Prompt Log 3: Petrophysical Heuristic Column Detection

* **Prompt:**
  > "Write a Python function to detect porosity and permeability column names in an arbitrary CSV uploaded by a petroleum engineer."
* **Purpose:**
  > To make the Rock & Fluid Dashboard resilient against different column naming conventions (e.g., `Porosity_percent`, `phi`, `PORO`, `Permeability_mD`, `k_mD`).
* **AI Output:**
  > Provided regex and list-matching heuristics against normalized lowercase string tokens.
* **Independent Verification:**
  > Tested against synthetic core analysis datasets and varied header formats.
* **Correction Applied:**
  > Added fallback UI dropdown selectors in Streamlit so users can manually map columns if custom or non-standard naming conventions are used.
* **Lesson Learned:**
  > Automated heuristics improve user experience, but engineering software must always provide manual override controls when parsing external experimental data.
