"""
Core Gamma-function logic (D2/Problem 5).

Rebuilds the Lanczos approximation from D1/Problem 4 so that the
calculation itself only uses our own homemade_ln / homemade_exp
helpers instead of Python's math module. Input parsing, formatting,
and comparisons still use ordinary Python (float(), f-strings), since
those are input/output/arithmetic, not the calculation being tested.

One shared parser (parse_calculation_lines) now covers three needs
that used to be three separate features:
  - a single argument on its own line          -> REQ-05 / REQ-06
  - one "argument, expected_value" line         -> REQ-14
  - several "argument, expected_value" lines    -> REQ-15
"""

from gamma_exceptions import GammaInputProblem, GammaRangeProblem
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

# Same approved test dataset from D1/Problem 2 (REQ-11). This list is
# fixed on purpose - it is the documented evidence for REQ-11 and does
# not change based on what the user types elsewhere in the program.
REFERENCE_VALUES = (
    (1.0, 1.0),
    (5.0, 24.0),
    (4.5, 11.6317283965668),
    (170.0, 4.269068009004705e304),
)


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


def _relative_gap(computed_value, expected_value):
    """Shared relative-error rule used by every accuracy/verification check."""
    if expected_value == 0.0:
        return size_of(computed_value - expected_value)
    return size_of(computed_value - expected_value) / size_of(expected_value)


def check_accuracy():
    """
    REQ-11: compare our result to the fixed, approved test dataset.

    This dataset never changes based on user input - it is separate
    from parse_calculation_lines / run_calculation_lines below.
    """
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
    """
    Parse a single, already-trimmed line into (argument, expected_value).

    expected_value is None when the line was just a plain argument.
    Raises GammaInputProblem (without a line number - the caller adds
    that) on anything unusable.
    """
    pieces = trimmed_line.split(",")
    if len(pieces) not in (1, 2):
        raise GammaInputProblem("use 'argument' or 'argument, expected_value'.")

    try:
        row_argument = float(pieces[0].strip())
        row_expected = float(pieces[1].strip()) if len(pieces) == 2 else None
    except ValueError as parse_error:
        raise GammaInputProblem("values must be numbers, such as 4.5 or 2e-3.") from parse_error

    if row_argument != row_argument:  # a NaN never equals itself
        raise GammaInputProblem("that argument is not usable.")

    if row_argument <= 0.0:
        raise GammaInputProblem("the argument must be greater than zero.")

    return row_argument, row_expected


def evaluate_lines(raw_text):
    """
    Evaluate every non-blank line on its own, independently.

    A line that fails to parse, or overflows during calculation,
    reports its own error and does NOT stop the remaining lines from
    still being evaluated - REQ-10 ("continue running after invalid
    input") applied per line rather than only across the whole session.

    Returns a list of (line_number, message_text, status) tuples,
    where status is one of "ok", "pass", "fail", "error". A plain
    argument line (REQ-05/06) gives "ok"; a line with an expected
    value gives "pass" or "fail" (REQ-14 for one such line, REQ-15
    for several); anything unusable gives "error".
    """
    line_results = []
    saw_any_content = False

    for line_number, raw_line in enumerate(raw_text.splitlines(), start=1):
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