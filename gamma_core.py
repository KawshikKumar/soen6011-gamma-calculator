"""
Core Gamma-function logic (D2/Problem 5).

Rebuilds the Lanczos approximation from D1/Problem 4 so that the
calculation itself only uses our own homemade_ln / homemade_exp
helpers instead of Python's math module. Input parsing, formatting,
and comparisons still use ordinary Python (float(), f-strings), since
those are input/output/arithmetic, not the calculation being tested.
"""

from gamma_exceptions import GammaInputProblem
from gamma_math_tools import homemade_ln, homemade_exp, size_of, CIRCLE_RATIO

# Same Lanczos g=7, n=9 coefficient table used and cited in D1
# (Lanczos, 1964; Press et al., Numerical Recipes, 3rd ed., section 6.1).
# Kept unchanged here on purpose: D2/Problem 5 asks to modify the D1
# implementation, not to re-pick a different algorithm.
LANCZOS_SHIFT = 7.0
LANCZOS_TABLE = (
    0.99999999999980993,
    676.5203681218851,
    -1259.1392167224028,
    771.32342877765313,
    -176.61502916214059,
    12.507343278686905,
    -0.13857109526572012,
    9.9843695780195716e-6,
    1.5056327351493116e-7,
)

# Same approved test dataset from D1/Problem 2 (REQ-11).
REFERENCE_VALUES = (
    (1.0, 1.0),
    (5.0, 24.0),
    (4.5, 11.6317283965668),
    (170.0, 4.269068009004705e304),
)


def read_positive_argument(raw_text):
    """
    Turn typed text into one positive real number.

    Mirrors REQ-01 / REQ-02 / REQ-03 / REQ-07 / REQ-08 / REQ-09
    from D1/Problem 2.
    """
    trimmed_text = raw_text.strip()

    if not trimmed_text:
        raise GammaInputProblem("Please type a value before calculating.")

    try:
        candidate_value = float(trimmed_text)
    except ValueError as parse_error:
        raise GammaInputProblem(
            "Please type a positive number, such as 4.5 or 2e-3."
        ) from parse_error

    if candidate_value != candidate_value:  # a NaN never equals itself
        raise GammaInputProblem("That is not a usable number.")

    if candidate_value <= 0.0:
        raise GammaInputProblem("The argument must be greater than zero.")

    return candidate_value


def gamma_from_scratch(argument):
    """Approximate Gamma(argument) using only our own ln/exp helpers."""
    working_argument = argument
    shift_correction = 0.0

    # Gamma(a + 1) = a * Gamma(a): shift small arguments up past 1
    # before applying the Lanczos formula.
    while working_argument < 1.0:
        shift_correction += homemade_ln(working_argument)
        working_argument += 1.0

    base_argument = working_argument - 1.0

    coefficient_total = LANCZOS_TABLE[0]
    for position in range(1, len(LANCZOS_TABLE)):
        coefficient_total += LANCZOS_TABLE[position] / (base_argument + position)

    scaled_base = base_argument + LANCZOS_SHIFT + 0.5

    log_gamma = (
        0.5 * homemade_ln(2.0 * CIRCLE_RATIO)
        + (base_argument + 0.5) * homemade_ln(scaled_base)
        - scaled_base
        + homemade_ln(coefficient_total)
        - shift_correction
    )

    return homemade_exp(log_gamma)


def format_with_digits(value, digit_count=7):
    """Turn a number into text with at least digit_count significant digits."""
    return f"{value:.{digit_count}g}"


def check_accuracy():
    """Return a list of text lines comparing our result to known values."""
    report_lines = []
    for test_argument, expected_value in REFERENCE_VALUES:
        computed_value = gamma_from_scratch(test_argument)
        if expected_value == 0.0:
            gap = size_of(computed_value - expected_value)
        else:
            gap = size_of(computed_value - expected_value) / size_of(expected_value)
        verdict = "PASS" if gap <= 1e-6 else "FAIL"
        report_lines.append(
            f"Gamma({format_with_digits(test_argument)}) = "
            f"{format_with_digits(computed_value)}  "
            f"(relative error {gap:.2e}) [{verdict}]"
        )
    return report_lines
