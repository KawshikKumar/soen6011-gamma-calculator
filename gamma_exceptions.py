"""
Custom exception classes for the from-scratch Gamma calculator (D2/Problem 5).

Writing our own exception types (instead of only using ValueError or
OverflowError directly) makes it obvious in the GUI code which kind of
problem happened: something the user typed, or something the
calculation itself could not handle.
"""


class GammaInputProblem(ValueError):
    """Raised when the text the user typed cannot be used as an argument."""
    pass


class GammaRangeProblem(OverflowError):
    """Raised when a Gamma result would be too large for this calculator."""
    pass
