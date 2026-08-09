"""
Home-made math helpers for the Gamma calculator.

Rebuilds absolute value, natural log, and exponential using only
addition, subtraction, multiplication, and division, so the Gamma
calculation does not depend on Python's math module.
"""

from gamma_exceptions import GammaRangeProblem

CIRCLE_RATIO = 3.14159265358979323846
UPPER_SAFE_LIMIT = 1.7e308
SERIES_STOP_POINT = 1e-18


def size_of(number):
    """Absolute value of a number."""
    if number < 0.0:
        return -number
    return number


def _log_series_near_one(value):
    """
    Natural log of a number close to 1.

    ln(value) = 2 * (w + w^3/3 + w^5/5 + ...),
    with w = (value - 1) / (value + 1).
    """
    w = (value - 1.0) / (value + 1.0)
    w_squared = w * w
    running_term = w
    running_total = 0.0
    term_index = 1
    while size_of(running_term) > SERIES_STOP_POINT:
        running_total += running_term / term_index
        running_term *= w_squared
        term_index += 2
    return 2.0 * running_total


_TWO_STEP_LOG = _log_series_near_one(2.0)


def homemade_ln(value):
    """Natural logarithm of a strictly positive number."""
    if value <= 0.0:
        raise GammaRangeProblem(
            "Cannot take a logarithm of a non-positive number."
        )

    doubling_count = 0
    shrunk_value = value

    while shrunk_value >= 2.0:
        shrunk_value /= 2.0
        doubling_count += 1
    while shrunk_value < 1.0:
        shrunk_value *= 2.0
        doubling_count -= 1

    near_one_part = _log_series_near_one(shrunk_value)
    return near_one_part + doubling_count * _TWO_STEP_LOG


def homemade_exp(value):
    """e raised to the power of value."""
    negative_input = value < 0.0
    working_value = -value if negative_input else value

    halving_steps = 0
    while working_value > 1.0:
        working_value /= 2.0
        halving_steps += 1

    running_term = 1.0
    running_total = 1.0
    term_index = 1
    while size_of(running_term) > SERIES_STOP_POINT:
        running_term *= working_value / term_index
        running_total += running_term
        term_index += 1

    result = running_total
    squaring_count = 0
    while squaring_count < halving_steps:
        result *= result
        if result > UPPER_SAFE_LIMIT:
            raise GammaRangeProblem(
                "This result is too large for the calculator to store."
            )
        squaring_count += 1

    if negative_input:
        result = 1.0 / result

    return result
