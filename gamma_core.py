"""
Core Gamma-function logic for the calculator.

Rebuilds the Lanczos approximation using only homemade_ln / homemade_exp
instead of Python's math module. One parser (evaluate_lines) covers
three cases per line: a plain argument, or an argument with an expected
value to compare against.
"""

from gamma_exceptions import GammaInputProblem, GammaRangeProblem
from gamma_math_tools import homemade_ln, homemade_exp, size_of, CIRCLE_RATIO

# Lanczos g=7, n=9 coefficient table (Lanczos, 1964; Press et al.,
# Numerical Recipes, 3rd ed., section 6.1).
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
LANCZOS_TERM_COUNT = 9

# Approved test dataset for REQ-11.
REFERENCE_VALUES = (
    (1.0, 1.0),
    (5.0, 24.0),
    (4.5, 11.6317283965668),
    (170.0, 4.269068009004705e304),
)


def _is_unusable_number(value):
    """True for NaN or infinity. A finite number times zero is always
    exactly zero; NaN or infinity times zero is not."""
    return (value * 0.0) != 0.0


def gamma_from_scratch(argument):
    """Approximate Gamma(argument)."""
    working_argument = argument
    shift_correction = 0.0

    while working_argument < 1.0:
        shift_correction += homemade_ln(working_argument)
        working_argument += 1.0

    base_argument = working_argument - 1.0

    coefficient_total = LANCZOS_TABLE[0]
    position = 1
    while position < LANCZOS_TERM_COUNT:
        coefficient_total += LANCZOS_TABLE[position] / (base_argument + position)
        position += 1

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
    """Format a number with at least digit_count significant digits."""
    return f"{value:.{digit_count}g}"


def _relative_gap(computed_value, expected_value):
    """Relative error between a computed value and an expected value."""
    if expected_value == 0.0:
        return size_of(computed_value - expected_value)
    return size_of(computed_value - expected_value) / size_of(expected_value)


def check_accuracy():
    """REQ-11: compare our result to the fixed, approved test dataset."""
    report_lines = []
    for test_argument, expected_value in REFERENCE_VALUES:
        computed_value = gamma_from_scratch(test_argument)
        gap = _relative_gap(computed_value, expected_value)
        verdict = "PASS" if gap <= 1e-6 else "FAIL"
        report_lines.append(
            f"Gamma({format_with_digits(test_argument)}) = "
            f"{format_with_digits(computed_value)}  "
            f"(relative error {gap:.2e}) [{verdict}]"
        )
    return report_lines


def _parse_one_line(trimmed_line):
    """Parse one line into (argument, expected_value). expected_value
    is None when the line was just a plain argument."""
    pieces = trimmed_line.split(",")
    piece_count = 0
    for _ in pieces:
        piece_count += 1

    if piece_count != 1 and piece_count != 2:
        raise GammaInputProblem("use 'argument' or 'argument, expected_value'.")

    try:
        row_argument = float(pieces[0].strip())
        row_expected = float(pieces[1].strip()) if piece_count == 2 else None
    except ValueError as parse_error:
        raise GammaInputProblem("values must be numbers, such as 4.5 or 2e-3.") from parse_error

    if _is_unusable_number(row_argument):
        raise GammaInputProblem("infinity and NaN are not supported as an argument.")

    if row_argument <= 0.0:
        raise GammaInputProblem("the argument must be greater than zero.")

    if row_expected is not None and _is_unusable_number(row_expected):
        raise GammaInputProblem("infinity and NaN are not supported as a reference value.")

    return row_argument, row_expected


def evaluate_lines(raw_text):
    """
    Evaluate every non-blank line on its own. A line that fails to
    parse, or overflows during calculation, reports its own error and
    does not stop the remaining lines from being evaluated.

    Returns a list of (line_number, message_text, status) tuples,
    status being one of "ok", "pass", "fail", "error".
    """
    line_results = []
    saw_any_content = False
    line_number = 0

    for raw_line in raw_text.splitlines():
        line_number += 1
        trimmed_line = raw_line.strip()
        if not trimmed_line:
            continue
        saw_any_content = True

        try:
            row_argument, row_expected = _parse_one_line(trimmed_line)
            computed_value = gamma_from_scratch(row_argument)
        except GammaInputProblem as input_error:
            line_results.append((line_number, f"Line {line_number}: {input_error}", "error"))
            continue
        except GammaRangeProblem as range_error:
            line_results.append((line_number, f"Line {line_number}: {range_error}", "error"))
            continue

        if row_expected is None:
            message = (
                f"Gamma({format_with_digits(row_argument)}) = "
                f"{format_with_digits(computed_value)}"
            )
            line_results.append((line_number, message, "ok"))
        else:
            gap = _relative_gap(computed_value, row_expected)
            status = "pass" if gap <= 1e-6 else "fail"
            verdict = "PASS" if status == "pass" else "FAIL"
            message = (
                f"Gamma({format_with_digits(row_argument)}) = "
                f"{format_with_digits(computed_value)}  vs your "
                f"{format_with_digits(row_expected)}  "
                f"(relative error {gap:.2e}) [{verdict}]"
            )
            line_results.append((line_number, message, status))

    if not saw_any_content:
        raise GammaInputProblem("Please enter at least one argument before calculating.")

    return line_results