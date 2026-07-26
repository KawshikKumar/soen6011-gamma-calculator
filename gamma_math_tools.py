"""
Home-made math helpers (D2/Problem 5).

Deliverable 2 does not allow calling Python's built-in math library
for the Gamma calculation. This file rebuilds the three pieces the
Gamma formula needs - an absolute value, a natural logarithm, and an
exponential - using nothing but addition, subtraction, multiplication,
and division.
"""

from gamma_exceptions import GammaRangeProblem

# Pi is written here as a plain number, the same way one would write
# 2 or 0.5 in a formula. It is a mathematical constant, not a call to
# a library function.
CIRCLE_RATIO = 3.14159265358979323846

# Anything bigger than this is treated as "too big for this calculator"
# (Python's own float type tops out a little under 1.8e308).
UPPER_SAFE_LIMIT = 1.7e308

# How many decimal places of precision each series should aim for
# before it stops adding more terms.
SERIES_STOP_POINT = 1e-18


def size_of(number):
    """Our own version of abs(): how far a number is from zero."""
    if number < 0.0:
        return -number
    return number


def _log_series_near_one(value):
    """
    Natural log of a number that is already close to 1.

    Uses the identity ln(value) = 2 * (w + w^3/3 + w^5/5 + ...),
    where w = (value - 1) / (value + 1). This only converges quickly
    when "value" is near 1, so callers must shrink it there first.
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


# ln(2) is produced once here, from our own series above, instead of
# being typed in as a memorized constant.
_TWO_STEP_LOG = _log_series_near_one(2.0)


def homemade_ln(value):
    """Return the natural logarithm of a strictly positive number."""
    if value <= 0.0:
        raise GammaRangeProblem("Cannot take a logarithm of a non-positive number.")

    doubling_count = 0
    shrunk_value = value

    # Push shrunk_value into the friendly window [1, 2) by repeatedly
    # halving or doubling it, and remember how many times we did so.
    while shrunk_value >= 2.0:
        shrunk_value /= 2.0
        doubling_count += 1
    while shrunk_value < 1.0:
        shrunk_value *= 2.0
        doubling_count -= 1

    return _log_series_near_one(shrunk_value) + doubling_count * _TWO_STEP_LOG


def homemade_exp(value):
    """Return e raised to the power of value, without using math.exp."""
    negative_input = value < 0.0
    working_value = -value if negative_input else value

    # Halve the value until it is small, so the series below converges
    # quickly. We remember how many halvings we did.
    halving_steps = 0
    while working_value > 1.0:
        working_value /= 2.0
        halving_steps += 1

    # Taylor series for e^x around 0: 1 + x + x^2/2! + x^3/3! + ...
    running_term = 1.0
    running_total = 1.0
    term_index = 1
    while size_of(running_term) > SERIES_STOP_POINT:
        running_term *= working_value / term_index
        running_total += running_term
        term_index += 1

    # Undo the halving from earlier by squaring the result the same
    # number of times: e^x = (e^(x / 2^n))^(2^n).
    result = running_total
    for _ in range(halving_steps):
        result *= result
        if result > UPPER_SAFE_LIMIT:
            raise GammaRangeProblem("This result is too large for the calculator to store.")

    if negative_input:
        result = 1.0 / result

    return result
