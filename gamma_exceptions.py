"""
Custom exception classes for the from-scratch Gamma calculator.

Writing our own exception types (instead of only using ValueError or
OverflowError directly) makes it obvious in the GUI code which kind
of problem happened: something the user typed, or something the
calculation itself could not handle.
"""


class GammaInputProblem(ValueError):
    """Raised when the typed text cannot be used as an argument."""


class GammaRangeProblem(OverflowError):
    """Raised when a result is too large for this calculator."""
