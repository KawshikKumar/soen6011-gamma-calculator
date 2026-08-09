"""
Unit tests for the from-scratch math helpers (D3/Problem 8).

These tests give confidence in the pieces the Gamma calculation is
built on: if homemade_ln or homemade_exp drift, every Gamma result
drifts with them. Expected values are written in as literal
constants so the tests do not depend on Python's math module.
"""

import unittest

# Pylint's missing-function-docstring check is switched off for this
# module only. unittest calls shortDescription() when it reports a
# result, so a docstring on a test method replaces the method name in
# the -v output. The method names are the specification of each test
# case and are what make the test report readable, so they are kept
# and the docstrings are deliberately omitted. The check stays active
# on every production module.
# pylint: disable=missing-function-docstring

from gamma_exceptions import GammaRangeProblem
from gamma_math_tools import (
    CIRCLE_RATIO,
    homemade_exp,
    homemade_ln,
    size_of,
)

# Literal reference constants, correct to double precision.
LN_2 = 0.6931471805599453
LN_10 = 2.302585092994046
LN_HALF = -0.6931471805599453
EULER_E = 2.718281828459045
EXP_MINUS_ONE = 0.36787944117144233
EXP_TEN = 22026.465794806718

HELPER_TOLERANCE = 1e-12


def relative_difference(computed, expected):
    """Relative difference, used only inside the tests."""
    if expected == 0.0:
        return abs(computed - expected)
    return abs(computed - expected) / abs(expected)


class SizeOfTests(unittest.TestCase):
    """size_of is the calculator's replacement for abs()."""

    def test_positive_value_is_unchanged(self):
        self.assertEqual(size_of(4.5), 4.5)

    def test_negative_value_becomes_positive(self):
        self.assertEqual(size_of(-4.5), 4.5)

    def test_zero_stays_zero(self):
        self.assertEqual(size_of(0.0), 0.0)


class HomemadeLnTests(unittest.TestCase):
    """Natural logarithm rebuilt from a series."""

    def test_ln_of_one_is_zero(self):
        self.assertAlmostEqual(homemade_ln(1.0), 0.0, places=12)

    def test_ln_of_two(self):
        gap = relative_difference(homemade_ln(2.0), LN_2)
        self.assertLessEqual(gap, HELPER_TOLERANCE)

    def test_ln_of_ten_uses_range_reduction(self):
        gap = relative_difference(homemade_ln(10.0), LN_10)
        self.assertLessEqual(gap, HELPER_TOLERANCE)

    def test_ln_below_one_is_negative(self):
        gap = relative_difference(homemade_ln(0.5), LN_HALF)
        self.assertLessEqual(gap, HELPER_TOLERANCE)

    def test_ln_of_a_very_large_number(self):
        # ln(1e300) = 300 * ln(10); exercises repeated halving.
        gap = relative_difference(homemade_ln(1e300), 300.0 * LN_10)
        self.assertLessEqual(gap, HELPER_TOLERANCE)

    def test_ln_of_zero_raises_range_problem(self):
        with self.assertRaises(GammaRangeProblem):
            homemade_ln(0.0)

    def test_ln_of_negative_raises_range_problem(self):
        with self.assertRaises(GammaRangeProblem):
            homemade_ln(-3.0)


class HomemadeExpTests(unittest.TestCase):
    """Exponential rebuilt from a series."""

    def test_exp_of_zero_is_one(self):
        self.assertAlmostEqual(homemade_exp(0.0), 1.0, places=12)

    def test_exp_of_one_is_e(self):
        gap = relative_difference(homemade_exp(1.0), EULER_E)
        self.assertLessEqual(gap, HELPER_TOLERANCE)

    def test_exp_of_negative_one(self):
        gap = relative_difference(homemade_exp(-1.0), EXP_MINUS_ONE)
        self.assertLessEqual(gap, HELPER_TOLERANCE)

    def test_exp_of_ten_uses_repeated_squaring(self):
        gap = relative_difference(homemade_exp(10.0), EXP_TEN)
        self.assertLessEqual(gap, HELPER_TOLERANCE)

    def test_exp_beyond_double_precision_raises_range_problem(self):
        with self.assertRaises(GammaRangeProblem):
            homemade_exp(1.0e6)


class HelperRoundTripTests(unittest.TestCase):
    """exp and ln should undo each other."""

    def test_exp_of_ln_returns_the_original_value(self):
        for value in (0.25, 1.0, 4.5, 170.0, 1e12):
            with self.subTest(value=value):
                recovered = homemade_exp(homemade_ln(value))
                gap = relative_difference(recovered, value)
                self.assertLessEqual(gap, 1e-11)


class CircleRatioTests(unittest.TestCase):
    """The Lanczos formula needs pi to full double precision."""

    def test_circle_ratio_matches_pi_to_double_precision(self):
        gap = relative_difference(CIRCLE_RATIO, 3.141592653589793)
        self.assertLessEqual(gap, 1e-15)


if __name__ == "__main__":
    unittest.main()
