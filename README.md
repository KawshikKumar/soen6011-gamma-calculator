# Galaxy Gamma Calculator

SOEN 6011 — Software Engineering Processes, Section CC, Summer 2026
Concordia University

Assigned transcendental function: **F4 — Γ(x), the Gamma function**

## What this is

A Gamma-function calculator built for **Cooper Brand**, a fictional
galaxy-luminosity astronomer proto-persona (see D1/Problem 1). Cooper
uses the calculator to independently verify Gamma-function values that
come up in galaxy-luminosity modelling, so the tool is built around
three needs: calculate a value, trust that the calculation is
accurate, and cross-check values Cooper already has from elsewhere.

The Gamma function is approximated using the **Lanczos approximation**
(g = 7, n = 9 terms), selected over a Stirling-approximation
alternative in D1/Problem 3-4 because it does not require the input to
already be large and better supports the full range of positive real
arguments Cooper works with.

As of D2/Problem 5, the implementation is **built from scratch**: it
does not call Python's `math` module. The natural logarithm and
exponential needed by the Lanczos formula are each implemented as
their own numerical series (see `gamma_math_tools.py`), verified
against `math.log` / `math.exp` during development to confirm
correctness before being relied on.

## Files

| File | Responsibility |
|---|---|
| `gamma_exceptions.py` | Two custom exception types: `GammaInputProblem` (bad user input) and `GammaRangeProblem` (a result too large to store). |
| `gamma_math_tools.py` | From-scratch `homemade_ln`, `homemade_exp`, and `size_of` (our own `abs`), plus the π constant used by the Lanczos formula. No `math` module import. |
| `gamma_core.py` | The Lanczos approximation itself (`gamma_from_scratch`), the fixed REQ-11 accuracy check (`check_accuracy`), and `evaluate_lines`, which parses and computes one or more user-typed lines independently, line by line. |
| `gamma_gui.py` | The Tkinter GUI. Run this file to start the program. |

There is no single "main" file separate from the GUI — `gamma_gui.py`
is the entry point.

## How to run it

Requires Python 3 with Tkinter (included in the standard Python
installer on Windows and macOS; on Linux, install with
`sudo apt install python3-tk` if it's missing).

1. Place all four `.py` files in the same folder.
2. From that folder, run:

   ```bash
   python gamma_gui.py
   ```

No IDE, build step, or external package is required.

## Using the calculator

The left-hand box accepts one or more lines. Each line is either:

- **a single positive number** — calculates Γ(x) and displays it
  (e.g. `4.5`)
- **`argument, expected_value`** — calculates Γ(argument) *and*
  compares it against `expected_value`, reporting a relative error and
  a PASS/FAIL verdict (e.g. `4.5, 11.6317`)

Multiple lines can be mixed freely. Clicking **Calculate** evaluates
every line independently — a mistake on one line is reported on that
line only and does not stop the other lines from still being
calculated. The **Run accuracy check** button separately verifies the
calculator against a fixed, previously-approved set of reference
values (unrelated to whatever is currently typed in the input box).

## Requirement traceability

Requirements originate from D1/Problem 2 and were updated for
D2/Problem 7 based on what D2/Problem 5's implementation added.

| ID | Requirement | Status |
|---|---|---|
| REQ-01 | Accept one positive real argument. | Unchanged |
| REQ-02 | Accept decimal and scientific notation. | Unchanged |
| REQ-03 | Validate the argument before calculation. | Unchanged |
| REQ-04 | Calculate the Gamma function for a valid argument. | Modified — now computed from scratch (no `math` module). |
| REQ-05 | Display the entered argument and calculated result together. | Modified — shown in the GUI result/log area instead of console text. |
| REQ-06 | Allow another calculation without restarting the program. | Unchanged in intent; now via GUI rather than a text loop. |
| REQ-07 | Specific message for empty input. | Unchanged |
| REQ-08 | Specific message for non-numeric input. | Unchanged |
| REQ-09 | Reject zero and negative arguments. | Unchanged |
| REQ-10 | Continue running after invalid input. | Modified — now applies per line within a multi-line batch, not just across separate runs. |
| REQ-11 | Relative error ≤ 1e-6 for the approved test dataset. | Unchanged dataset; verified in practice at ~1e-12 to 1e-13. |
| REQ-12 | Present the result with at least seven significant digits. | Unchanged |
| REQ-13 | Specific message for arguments beyond the supported range. | Unchanged |
| REQ-14 | Allow the user to supply a reference value and see the relative error of a calculated result against it. | New in D2 — elaborates Cooper's D1 persona task "checks whether numerical results are accurate." |
| REQ-15 | Allow the user to verify multiple previously computed argument/expected-value pairs in one session. | New in D2 — elaborates Cooper's D1 persona description "verifies numerical results... cross-checks results." |

## Known limitations

- Supported argument range extends up to the double-precision overflow
  limit (approximately x ≈ 171.6); larger arguments raise
  `GammaRangeProblem` (A-05, REQ-13).
- The calculator only computes Γ(x) for positive real x; it does not
  process astronomy datasets or files (A-03).

## Verification approach

`homemade_ln` and `homemade_exp` were checked against Python's
`math.log`/`math.exp` during development (not at runtime, to keep the
from-scratch constraint intact), and `gamma_from_scratch` was checked
against the same approved test dataset used for REQ-11
(Γ(1), Γ(5), Γ(4.5), Γ(170)), all within ~1e-12 to 1e-13 relative
error — well inside the 1e-6 requirement.

## References

- Lanczos, C., "A Precision Approximation of the Gamma Function," 1964.
- Press, W. H., Teukolsky, S. A., Vetterling, W. T., Flannery, B. P.,
  *Numerical Recipes: The Art of Scientific Computing*, 3rd ed., §6.1,
  Cambridge University Press, 2007.
- NIST Digital Library of Mathematical Functions, §5.2, §5.5, §5.11 —
  Gamma function definitions, functional relations, asymptotic
  expansions.
- ISO/IEC/IEEE 29148:2018, Requirements Engineering.
- Turner, A. M., Reeder, B., Ramey, J., "Scenarios, Personas and User
  Stories," 2013.
- Zaninetti, L., "The Luminosity Function of Galaxies as Modelled by
  the Generalized Gamma Distribution," arXiv:1004.4776, 2010.
