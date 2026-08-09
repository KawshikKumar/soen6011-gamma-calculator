"""
Unit tests for the Gamma calculation and the line parser
(D3/Problem 8).

Test cases are traced to the current D2 requirement list
(REQ-01 to REQ-15). Expected Gamma values are written in as literal
constants taken from published values, so the tests do not use
Python's math module and do not re-use the code under test as its
own reference.
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

from gamma_core import (
    ACCURACY_TOLERANCE,
    REFERENCE_VALUES,
    _is_unusable_number,
    _parse_one_line,
    _relative_gap,
    check_accuracy,
    evaluate_lines,
    format_with_digits,
    gamma_from_scratch,
)
from gamma_exceptions import GammaInputProblem, GammaRangeProblem

# Published Gamma values, correct to double precision.
GAMMA_OF_ONE = 1.0
GAMMA_OF_FIVE = 24.0
GAMMA_OF_FOUR_POINT_FIVE = 11.631728396567448
GAMMA_OF_ONE_SEVENTY = 4.269068009004705e304
GAMMA_OF_HALF = 1.772453850905516
GAMMA_OF_ONE_POINT_FIVE = 0.8862269254527580
GAMMA_OF_SEVEN = 720.0

# An argument large enough that the result cannot be stored in a
# double (Gamma overflows a little past 171.6).
UNSUPPORTED_ARGUMENT = 200.0


def relative_difference(computed, expected):
    """Relative difference, used only inside the tests."""
    if expected == 0.0:
        return abs(computed - expected)
    return abs(computed - expected) / abs(expected)


class ApprovedDatasetTests(unittest.TestCase):
    """REQ-11: relative error must stay at or below 1e-6 on the
    approved dataset Gamma(1), Gamma(5), Gamma(4.5), Gamma(170)."""

    def test_gamma_of_one(self):
        gap = relative_difference(
            gamma_from_scratch(1.0), GAMMA_OF_ONE
        )
        self.assertLessEqual(gap, ACCURACY_TOLERANCE)

    def test_gamma_of_five(self):
        gap = relative_difference(
            gamma_from_scratch(5.0), GAMMA_OF_FIVE
        )
        self.assertLessEqual(gap, ACCURACY_TOLERANCE)

    def test_gamma_of_four_point_five(self):
        gap = relative_difference(
            gamma_from_scratch(4.5), GAMMA_OF_FOUR_POINT_FIVE
        )
        self.assertLessEqual(gap, ACCURACY_TOLERANCE)

    def test_gamma_of_one_hundred_seventy(self):
        gap = relative_difference(
            gamma_from_scratch(170.0), GAMMA_OF_ONE_SEVENTY
        )
        self.assertLessEqual(gap, ACCURACY_TOLERANCE)

    def test_stored_dataset_still_holds_the_four_agreed_values(self):
        arguments = []
        for argument, _expected in REFERENCE_VALUES:
            arguments.append(argument)
        self.assertEqual(arguments, [1.0, 5.0, 4.5, 170.0])

    def test_check_accuracy_reports_a_pass_for_every_value(self):
        report_lines = check_accuracy()
        self.assertEqual(len(report_lines), 4)
        for line in report_lines:
            with self.subTest(line=line):
                self.assertIn("[PASS]", line)


class OtherPositiveArgumentTests(unittest.TestCase):
    """REQ-01/REQ-04: positive real arguments beyond the approved
    dataset, including values below 1."""

    def test_gamma_below_one_uses_the_recurrence_shift(self):
        gap = relative_difference(
            gamma_from_scratch(0.5), GAMMA_OF_HALF
        )
        self.assertLessEqual(gap, ACCURACY_TOLERANCE)

    def test_gamma_of_a_decimal_above_one(self):
        gap = relative_difference(
            gamma_from_scratch(1.5), GAMMA_OF_ONE_POINT_FIVE
        )
        self.assertLessEqual(gap, ACCURACY_TOLERANCE)

    def test_gamma_of_another_positive_integer(self):
        gap = relative_difference(
            gamma_from_scratch(7.0), GAMMA_OF_SEVEN
        )
        self.assertLessEqual(gap, ACCURACY_TOLERANCE)

    def test_gamma_satisfies_the_recurrence_relation(self):
        # Gamma(x + 1) = x * Gamma(x), an independent property check.
        for argument in (0.25, 1.3, 6.0, 20.5):
            with self.subTest(argument=argument):
                left = gamma_from_scratch(argument + 1.0)
                right = argument * gamma_from_scratch(argument)
                gap = relative_difference(left, right)
                self.assertLessEqual(gap, ACCURACY_TOLERANCE)


class RangeBehaviourTests(unittest.TestCase):
    """REQ-13: arguments whose result cannot be stored."""

    def test_argument_beyond_the_supported_range(self):
        with self.assertRaises(GammaRangeProblem):
            gamma_from_scratch(UNSUPPORTED_ARGUMENT)

    def test_argument_just_inside_the_supported_range(self):
        result = gamma_from_scratch(171.0)
        self.assertGreater(result, 0.0)

    def test_out_of_range_line_reports_an_error_not_a_crash(self):
        results = evaluate_lines(str(UNSUPPORTED_ARGUMENT))
        self.assertEqual(len(results), 1)
        _line_number, message, status = results[0]
        self.assertEqual(status, "error")
        self.assertIn("too large", message)


class FormattingTests(unittest.TestCase):
    """REQ-12: at least seven significant digits."""

    def test_default_formatting_keeps_seven_significant_digits(self):
        text = format_with_digits(11.631728396567448)
        self.assertEqual(text, "11.63173")

    def test_digit_count_can_be_raised(self):
        text = format_with_digits(11.631728396567448, 12)
        self.assertEqual(text, "11.6317283966")

    def test_large_values_are_shown_in_scientific_notation(self):
        text = format_with_digits(GAMMA_OF_ONE_SEVENTY)
        self.assertIn("e+", text)


class RelativeGapTests(unittest.TestCase):
    """The comparison arithmetic behind REQ-11 and REQ-14."""

    def test_identical_values_have_no_gap(self):
        self.assertEqual(_relative_gap(24.0, 24.0), 0.0)

    def test_gap_is_relative_to_the_expected_value(self):
        self.assertAlmostEqual(_relative_gap(102.0, 100.0), 0.02)

    def test_gap_is_never_negative(self):
        self.assertAlmostEqual(_relative_gap(98.0, 100.0), 0.02)

    def test_zero_expected_value_falls_back_to_absolute_gap(self):
        self.assertEqual(_relative_gap(0.5, 0.0), 0.5)


class UnusableNumberTests(unittest.TestCase):
    """The arithmetic test used instead of math.isfinite."""

    def test_ordinary_numbers_are_usable(self):
        for value in (0.0, -3.5, 4.5, 1e300):
            with self.subTest(value=value):
                self.assertFalse(_is_unusable_number(value))

    def test_infinity_is_unusable(self):
        self.assertTrue(_is_unusable_number(float("inf")))

    def test_negative_infinity_is_unusable(self):
        self.assertTrue(_is_unusable_number(float("-inf")))

    def test_not_a_number_is_unusable(self):
        self.assertTrue(_is_unusable_number(float("nan")))


class LineParserTests(unittest.TestCase):
    """REQ-01/REQ-02/REQ-03: what one typed line is allowed to be."""

    def test_positive_integer(self):
        self.assertEqual(_parse_one_line("5"), (5.0, None))

    def test_positive_decimal(self):
        self.assertEqual(_parse_one_line("4.5"), (4.5, None))

    def test_scientific_notation(self):
        self.assertEqual(_parse_one_line("2e-3"), (0.002, None))

    def test_scientific_notation_with_a_capital_exponent(self):
        self.assertEqual(_parse_one_line("2E3"), (2000.0, None))

    def test_surrounding_whitespace_is_ignored(self):
        self.assertEqual(_parse_one_line("  4.5  "), (4.5, None))

    def test_argument_and_reference_pair(self):
        self.assertEqual(_parse_one_line("5, 24"), (5.0, 24.0))

    def test_reference_pair_without_a_space(self):
        self.assertEqual(_parse_one_line("5,24"), (5.0, 24.0))

    def test_reference_value_may_use_scientific_notation(self):
        argument, expected = _parse_one_line("170, 4.269068e304")
        self.assertEqual(argument, 170.0)
        self.assertAlmostEqual(
            expected / 4.269068e304, 1.0, places=12
        )


class InvalidInputTests(unittest.TestCase):
    """REQ-07/REQ-08/REQ-09: specific problems, specific messages,
    all raised as GammaInputProblem."""

    def test_nonnumeric_input(self):
        with self.assertRaises(GammaInputProblem):
            _parse_one_line("abc")

    def test_zero_is_rejected(self):
        with self.assertRaises(GammaInputProblem) as caught:
            _parse_one_line("0")
        self.assertIn("greater than zero", str(caught.exception))

    def test_negative_argument_is_rejected(self):
        with self.assertRaises(GammaInputProblem) as caught:
            _parse_one_line("-2.5")
        self.assertIn("greater than zero", str(caught.exception))

    def test_infinity_as_argument_is_rejected(self):
        with self.assertRaises(GammaInputProblem) as caught:
            _parse_one_line("inf")
        self.assertIn("infinity", str(caught.exception))

    def test_negative_infinity_as_argument_is_rejected(self):
        with self.assertRaises(GammaInputProblem):
            _parse_one_line("-inf")

    def test_not_a_number_as_argument_is_rejected(self):
        with self.assertRaises(GammaInputProblem) as caught:
            _parse_one_line("nan")
        self.assertIn("NaN", str(caught.exception))

    def test_infinity_as_reference_value_is_rejected(self):
        with self.assertRaises(GammaInputProblem) as caught:
            _parse_one_line("5, inf")
        self.assertIn("reference value", str(caught.exception))

    def test_missing_reference_value_after_the_comma(self):
        with self.assertRaises(GammaInputProblem):
            _parse_one_line("5,")

    def test_extra_comma_is_rejected(self):
        with self.assertRaises(GammaInputProblem) as caught:
            _parse_one_line("5, 24, 30")
        self.assertIn("expected_value", str(caught.exception))

    def test_nonnumeric_reference_value(self):
        with self.assertRaises(GammaInputProblem):
            _parse_one_line("5, twenty-four")

    def test_empty_input_is_rejected(self):
        with self.assertRaises(GammaInputProblem) as caught:
            evaluate_lines("")
        self.assertIn("at least one argument", str(caught.exception))

    def test_whitespace_only_input_is_rejected(self):
        with self.assertRaises(GammaInputProblem):
            evaluate_lines("   \n\t\n  ")

    def test_input_problem_is_a_value_error(self):
        self.assertTrue(issubclass(GammaInputProblem, ValueError))

    def test_range_problem_is_an_overflow_error(self):
        self.assertTrue(issubclass(GammaRangeProblem, OverflowError))


class SingleLineEvaluationTests(unittest.TestCase):
    """REQ-05: the argument and the result are reported together."""

    def test_plain_line_reports_argument_and_result(self):
        results = evaluate_lines("4.5")
        self.assertEqual(len(results), 1)
        line_number, message, status = results[0]
        self.assertEqual(line_number, 1)
        self.assertEqual(status, "ok")
        self.assertIn("Gamma(4.5)", message)
        self.assertIn("11.63173", message)

    def test_blank_lines_are_skipped_but_numbering_is_kept(self):
        results = evaluate_lines("\n\n5")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 3)


class ReferenceComparisonTests(unittest.TestCase):
    """REQ-14: compare a result against a value the user supplies."""

    def test_matching_reference_value_passes(self):
        results = evaluate_lines("5, 24")
        _line_number, message, status = results[0]
        self.assertEqual(status, "pass")
        self.assertIn("[PASS]", message)
        self.assertIn("vs your", message)

    def test_reference_value_within_tolerance_still_passes(self):
        # 24.000001 is about 4e-8 away, inside the 1e-6 tolerance.
        _line_number, _message, status = evaluate_lines(
            "5, 24.000001"
        )[0]
        self.assertEqual(status, "pass")

    def test_clearly_wrong_reference_value_fails(self):
        results = evaluate_lines("5, 30")
        _line_number, message, status = results[0]
        self.assertEqual(status, "fail")
        self.assertIn("[FAIL]", message)

    def test_reference_value_just_outside_tolerance_fails(self):
        # 24.0001 is about 4e-6 away, outside the 1e-6 tolerance.
        _line_number, _message, status = evaluate_lines("5, 24.0001")[0]
        self.assertEqual(status, "fail")

    def test_failed_comparison_still_shows_the_calculated_value(self):
        _line_number, message, _status = evaluate_lines("5, 30")[0]
        self.assertIn("Gamma(5) = 24", message)


class BatchEvaluationTests(unittest.TestCase):
    """REQ-15 and REQ-10: several pairs at once, and one bad line
    must not destroy the good lines around it."""

    def test_several_pairs_are_verified_in_one_call(self):
        results = evaluate_lines("1, 1\n5, 24\n4.5, 11.6317283966")
        self.assertEqual(len(results), 3)
        for _line_number, _message, status in results:
            self.assertEqual(status, "pass")

    def test_plain_and_comparison_lines_can_be_mixed(self):
        results = evaluate_lines("4.5\n5, 24")
        self.assertEqual(results[0][2], "ok")
        self.assertEqual(results[1][2], "pass")

    def test_a_bad_line_does_not_stop_the_good_lines(self):
        results = evaluate_lines("5, 24\nabc\n1, 1")
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][2], "pass")
        self.assertEqual(results[1][2], "error")
        self.assertEqual(results[2][2], "pass")

    def test_error_lines_name_the_line_they_came_from(self):
        results = evaluate_lines("5, 24\nabc\n1, 1")
        self.assertTrue(results[1][1].startswith("Line 2:"))

    def test_a_mixture_of_every_outcome_is_reported_line_by_line(self):
        results = evaluate_lines("4.5\n5, 24\n5, 30\n-1\n200")
        statuses = []
        for _line_number, _message, status in results:
            statuses.append(status)
        self.assertEqual(
            statuses, ["ok", "pass", "fail", "error", "error"]
        )


class RepeatedUseTests(unittest.TestCase):
    """REQ-06: the same logic can be called again and again without
    being reset, which is what the GUI relies on."""

    def test_repeated_calls_give_the_same_answer(self):
        first = evaluate_lines("4.5")[0][1]
        second = evaluate_lines("4.5")[0][1]
        self.assertEqual(first, second)

    def test_a_failing_call_does_not_disturb_the_next_one(self):
        with self.assertRaises(GammaInputProblem):
            evaluate_lines("")
        _line_number, _message, status = evaluate_lines("5, 24")[0]
        self.assertEqual(status, "pass")


if __name__ == "__main__":
    unittest.main()
