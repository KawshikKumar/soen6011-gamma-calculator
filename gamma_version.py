"""
Single source of truth for the calculator's version number.

The project follows Semantic Versioning (MAJOR.MINOR.PATCH):

    MAJOR   an incompatible change to how the calculator is used
    MINOR   new behaviour that does not break existing use
    PATCH   a correction that does not break existing use

1.0.0 is the D2/Problem 5 state: the from-scratch Lanczos
calculation, the Tkinter interface, the custom exception classes,
and REQ-01 through REQ-15.

1.1.0 is the D3/Problem 7 state. The calculation itself is
unchanged, so the MAJOR number stays at 1. The interface gains
keyboard operation, a textual status line, readable defaults and a
visible version, which is new behaviour that does not break any
existing way of using the calculator, so the MINOR number moves up
and PATCH resets to 0.

Every other file reads the version from here, so there is only one
place to edit when it changes.
"""

__version__ = "1.1.0"

VERSION_LABEL = "v" + __version__
