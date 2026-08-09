"""
Tkinter front end for the from-scratch Gamma calculator.

Single input box on the left accepts one or more lines: a plain
argument (REQ-05/06) or "argument, expected_value" to check against a
value Cooper already trusts (REQ-14 for one line, REQ-15 for
several). The session log sits on the right so results build up next
to the input instead of underneath it.

Run this file to start the program:
    python gamma_gui.py
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from gamma_core import check_accuracy, evaluate_lines
from gamma_exceptions import GammaInputProblem
from gamma_version import VERSION_LABEL

# A quiet, low-contrast palette - a plain dark editor look rather
# than a bright theme, so the numbers are what stands out. Colour is
# never the only carrier of meaning: every result line also starts
# with a word (RESULT, PASS, FAIL, ERROR).
BACKDROP = "#21242b"        # window background
PANEL_SHADE = "#2a2e37"     # input box / log background
LINE_EDGE = "#3a3f4b"       # subtle borders
FOCUS_EDGE = "#8fc3e0"      # border of whatever currently has focus
TEXT_PRIMARY = "#e4e6eb"    # normal readable text
TEXT_SECONDARY = "#b3b8c4"  # hints and labels, still readable
ACCENT = "#6fa8c9"          # single muted accent, used sparingly
GOOD_SIGNAL = "#8fc48f"     # PASS lines
BAD_SIGNAL = "#d09292"      # FAIL / error lines

# Font sizes are set once here. The smallest text in the window is
# 10 point, so no part of the interface depends on reading 8 point
# text.
BODY_SIZE = 11
HINT_SIZE = 10
TITLE_SIZE = 16
HEADING_SIZE = 11

# Font names differ between operating systems. Tk silently
# substitutes an unknown family, which makes the layout unpredictable,
# so we ask Tk which families actually exist and take the first one we
# recognise.
INTERFACE_FONT_CHOICES = (
    "Ubuntu", "Cantarell", "DejaVu Sans", "Noto Sans",
    "Segoe UI", "Helvetica",
)
NUMBER_FONT_CHOICES = (
    "Ubuntu Mono", "DejaVu Sans Mono", "Liberation Mono",
    "Noto Sans Mono", "Consolas", "Courier",
)

EXAMPLE_INPUT_TEXT = (
    "4.5            one value\n"
    "5, 24          one value, checked against 24\n"
    "2e-3           scientific notation"
)

READY_STATUS = "Ready. Type one or more lines, then Calculate."


def _first_available_font(candidate_names, fallback_name):
    """Return the first font family Tk actually has installed."""
    installed_families = set(tkfont.families())
    for candidate in candidate_names:
        if candidate in installed_families:
            return candidate
    return fallback_name


class GammaWindow:
    """Holds every widget for the calculator window."""

    def __init__(self, root_window):
        self.root_window = root_window
        root_window.title(f"Galaxy Gamma Calculator {VERSION_LABEL}")
        root_window.configure(background=BACKDROP)
        root_window.geometry("900x680")
        root_window.minsize(820, 640)

        # Both families are kept in one dictionary so the class does
        # not accumulate a separate attribute per font.
        self.fonts = {
            "interface": _first_available_font(
                INTERFACE_FONT_CHOICES, "TkDefaultFont"
            ),
            "number": _first_available_font(
                NUMBER_FONT_CHOICES, "TkFixedFont"
            ),
        }
        self.status_message = tk.StringVar(value=READY_STATUS)

        # Declared here so every attribute of the window is visible in
        # one place; the build methods below fill them in.
        self.input_box = None
        self.log_box = None
        self.calculate_button = None
        self.accuracy_button = None

        self._build_style()
        self._build_layout()
        self._build_key_bindings()

        self.input_box.focus_set()

    # -----------------------------------------------------------
    # Look and feel
    # -----------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self.root_window)
        style.theme_use("clam")

        style.configure("Sky.TFrame", background=BACKDROP)
        style.configure("Panel.TFrame", background=PANEL_SHADE)

        style.configure(
            "Title.TLabel", background=BACKDROP,
            foreground=TEXT_PRIMARY,
            font=(self.fonts["interface"], TITLE_SIZE, "bold"),
        )
        style.configure(
            "Subtitle.TLabel", background=BACKDROP,
            foreground=TEXT_SECONDARY,
            font=(self.fonts["interface"], HINT_SIZE),
        )
        style.configure(
            "Field.TLabel", background=BACKDROP,
            foreground=TEXT_PRIMARY,
            font=(self.fonts["interface"], BODY_SIZE),
        )
        style.configure(
            "Hint.TLabel", background=BACKDROP,
            foreground=TEXT_SECONDARY,
            font=(self.fonts["interface"], HINT_SIZE),
        )
        style.configure(
            "SectionHeading.TLabel", background=BACKDROP,
            foreground=TEXT_PRIMARY,
            font=(self.fonts["interface"], HEADING_SIZE, "bold"),
        )
        style.configure(
            "Status.TLabel", background=PANEL_SHADE,
            foreground=TEXT_PRIMARY,
            font=(self.fonts["interface"], BODY_SIZE),
            padding=8,
        )

        # Generous padding keeps the click targets large and well
        # separated (Fitts' Law), and Calculate is the only filled
        # button so the primary action stands out (Von Restorff).
        style.configure(
            "Primary.TButton", background=ACCENT, foreground=BACKDROP,
            font=(self.fonts["interface"], BODY_SIZE, "bold"),
            padding=(20, 12), borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#89bcd9"), ("focus", "#89bcd9")],
        )

        style.configure(
            "Quiet.TButton", background=PANEL_SHADE,
            foreground=TEXT_PRIMARY,
            font=(self.fonts["interface"], BODY_SIZE),
            padding=(16, 10), borderwidth=1,
        )
        style.map(
            "Quiet.TButton",
            background=[("active", "#343945")],
            bordercolor=[("focus", FOCUS_EDGE)],
        )

    # -----------------------------------------------------------
    # Layout
    # -----------------------------------------------------------
    def _build_layout(self):
        self.root_window.columnconfigure(0, weight=1, uniform="half")
        self.root_window.columnconfigure(1, weight=1, uniform="half")
        self.root_window.rowconfigure(0, weight=1)

        left_column = ttk.Frame(
            self.root_window, style="Sky.TFrame", padding=18
        )
        left_column.grid(row=0, column=0, sticky="nsew")

        right_column = ttk.Frame(
            self.root_window, style="Sky.TFrame",
            padding=(0, 18, 18, 18),
        )
        right_column.grid(row=0, column=1, sticky="nsew")

        self._build_input_panel(left_column)
        self._build_log_panel(right_column)

    def _build_heading(self, parent):
        ttk.Label(
            parent, text="Galaxy Gamma Calculator",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            parent,
            text=(
                "Gamma-function checks for galaxy-luminosity "
                f"research. Lanczos, from scratch. {VERSION_LABEL}"
            ),
            style="Subtitle.TLabel", justify="left", wraplength=340,
        ).pack(anchor="w", pady=(2, 14))

    def _build_input_area(self, parent):
        ttk.Label(
            parent, text="Enter one or more lines:",
            style="Field.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            parent,
            text=(
                "One line per value. A single number calculates "
                "Gamma. A number, then a comma, then a value you "
                "already trust also checks the result."
            ),
            style="Hint.TLabel", justify="left", wraplength=340,
        ).pack(anchor="w", pady=(0, 4))
        ttk.Label(
            parent, text=EXAMPLE_INPUT_TEXT, style="Hint.TLabel",
            justify="left", font=(self.fonts["number"], HINT_SIZE),
        ).pack(anchor="w", pady=(0, 8))

        input_frame = ttk.Frame(parent, style="Panel.TFrame", padding=2)
        input_frame.pack(fill="x")
        self.input_box = tk.Text(
            input_frame, height=7, wrap="none",
            background=PANEL_SHADE, foreground=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, borderwidth=0,
            highlightthickness=2, highlightbackground=LINE_EDGE,
            highlightcolor=FOCUS_EDGE,
            font=(self.fonts["number"], BODY_SIZE), padx=8, pady=8,
        )
        self.input_box.pack(fill="x")

    def _build_button_row(self, parent):
        button_row = ttk.Frame(parent, style="Sky.TFrame")
        button_row.pack(fill="x", pady=(12, 6))

        self.calculate_button = ttk.Button(
            button_row, text="Calculate", style="Primary.TButton",
            command=self.on_calculate_clicked,
        )
        self.calculate_button.pack(side="left", padx=(0, 10))

        clear_button = ttk.Button(
            button_row, text="Clear input", style="Quiet.TButton",
            command=self.on_clear_clicked,
        )
        clear_button.pack(side="left")

        ttk.Label(
            parent,
            text=(
                "Keyboard: Ctrl+Enter calculates, Tab moves to the "
                "next control, Escape clears the input."
            ),
            style="Hint.TLabel", justify="left", wraplength=340,
        ).pack(anchor="w")

    def _build_accuracy_area(self, parent):
        ttk.Separator(parent).pack(fill="x", pady=(12, 12))

        ttk.Label(
            parent, text="Approved test dataset (REQ-11)",
            style="SectionHeading.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            parent,
            text=(
                "A fixed set of known-correct values, unrelated to "
                "what you type above."
            ),
            style="Hint.TLabel", justify="left", wraplength=340,
        ).pack(anchor="w", pady=(0, 8))
        self.accuracy_button = ttk.Button(
            parent, text="Run accuracy check", style="Quiet.TButton",
            command=self.on_accuracy_clicked,
        )
        self.accuracy_button.pack(anchor="w")

    def _build_input_panel(self, parent):
        self._build_heading(parent)
        self._build_input_area(parent)
        self._build_button_row(parent)
        self._build_accuracy_area(parent)

    def _build_log_panel(self, parent):
        ttk.Label(
            parent, text="Session log", style="SectionHeading.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            parent,
            text="Every calculation and check you run appears here.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(0, 6))

        log_frame = ttk.Frame(parent, style="Panel.TFrame", padding=2)
        log_frame.pack(fill="both", expand=True)

        self.log_box = tk.Text(
            log_frame, wrap="word", state="disabled",
            background=PANEL_SHADE, foreground=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, borderwidth=0,
            highlightthickness=2, highlightbackground=LINE_EDGE,
            highlightcolor=FOCUS_EDGE,
            font=(self.fonts["number"], HINT_SIZE), padx=10, pady=10,
        )
        self.log_box.pack(fill="both", expand=True)
        self.log_box.tag_configure("good_line", foreground=GOOD_SIGNAL)
        self.log_box.tag_configure("bad_line", foreground=BAD_SIGNAL)
        self.log_box.tag_configure(
            "normal_line", foreground=TEXT_PRIMARY
        )

        # The status line repeats the outcome in words, directly under
        # the log, so the state of the program is never carried by
        # colour alone.
        status_frame = ttk.Frame(parent, style="Panel.TFrame")
        status_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(
            status_frame, textvariable=self.status_message,
            style="Status.TLabel", justify="left", wraplength=340,
        ).pack(anchor="w", fill="x")

    # -----------------------------------------------------------
    # Keyboard operation
    # -----------------------------------------------------------
    def _build_key_bindings(self):
        # Enter inserts a newline, because the box is multi-line, so
        # Ctrl+Enter is the calculate shortcut instead.
        self.input_box.bind(
            "<Control-Return>", self._calculate_from_keyboard
        )
        self.root_window.bind(
            "<Control-Return>", self._calculate_from_keyboard
        )
        self.root_window.bind("<Escape>", self._clear_from_keyboard)
        # A Text widget swallows Tab by default; forwarding it keeps
        # the focus order input box -> Calculate -> Clear input ->
        # Run accuracy check predictable for keyboard users.
        self.input_box.bind("<Tab>", self._move_focus_forward)
        self.input_box.bind("<Shift-Tab>", self._move_focus_backward)

    def _calculate_from_keyboard(self, _event=None):
        self.on_calculate_clicked()
        return "break"

    def _clear_from_keyboard(self, _event=None):
        self.on_clear_clicked()
        return "break"

    def _move_focus_forward(self, _event=None):
        self.calculate_button.focus_set()
        return "break"

    def _move_focus_backward(self, _event=None):
        self.accuracy_button.focus_set()
        return "break"

    # -----------------------------------------------------------
    # Behaviour
    # -----------------------------------------------------------
    def set_status(self, message_text):
        """Show the current state of the program in plain words."""
        self.status_message.set(message_text)

    def write_to_log(self, message_line, tag_name="normal_line"):
        """Append one line to the session log and scroll to it."""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message_line + "\n", tag_name)
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def _tag_for_line(self, line_text):
        if "[PASS]" in line_text:
            return "good_line"
        if "[FAIL]" in line_text:
            return "bad_line"
        return "normal_line"

    def _write_result_line(self, message, status):
        """Write one result line, prefixed with its status in words."""
        if status == "error":
            self.write_to_log("ERROR   " + message, "bad_line")
        elif status == "pass":
            self.write_to_log("PASS    " + message, "good_line")
        elif status == "fail":
            self.write_to_log("FAIL    " + message, "bad_line")
        else:
            self.write_to_log("RESULT  " + message, "normal_line")

    @staticmethod
    def _summary_text(plain_count, pass_count, checked_count,
                      error_count):
        """Build the wording used for both the log and the status
        line."""
        parts = []
        if plain_count:
            parts.append(f"{plain_count} value(s) calculated")
        if checked_count:
            parts.append(
                f"{pass_count} of {checked_count} checks passed"
            )
        if error_count:
            parts.append(f"{error_count} line(s) had errors")
        if not parts:
            return "Nothing to report."
        return "; ".join(parts) + "."

    def on_calculate_clicked(self):
        """
        REQ-05/06/10: shows argument+result together, allows repeats,
        keeps running after invalid input - per line, not just per
        session, so one bad line does not hide the good ones around
        it. Also covers REQ-14 (one compare line) and REQ-15 (several
        compare lines) through the same box, depending on what the
        user typed.
        """
        raw_text = self.input_box.get("1.0", "end")
        self.write_to_log("--- Calculate ---")
        self.set_status("Calculating...")
        self.root_window.update_idletasks()

        try:
            line_results = evaluate_lines(raw_text)
        except GammaInputProblem as input_error:
            # Only raised when there was nothing usable at all.
            self.write_to_log(f"ERROR   {input_error}", "bad_line")
            self.set_status(f"Nothing calculated: {input_error}")
            self.input_box.focus_set()
            return

        plain_count = 0
        pass_count = 0
        checked_count = 0
        error_count = 0

        for _line_number, message, status in line_results:
            if status == "error":
                error_count += 1
            elif status == "pass":
                pass_count += 1
                checked_count += 1
            elif status == "fail":
                checked_count += 1
            else:
                plain_count += 1
            self._write_result_line(message, status)

        summary = self._summary_text(
            plain_count, pass_count, checked_count, error_count
        )
        self.write_to_log("Summary: " + summary)
        self.set_status("Calculation finished. " + summary)

    def on_clear_clicked(self):
        """Empty the input box for a fresh set of lines. The session
        log is deliberately left alone, so no earlier work is lost."""
        self.input_box.delete("1.0", "end")
        self.input_box.focus_set()
        self.set_status(
            "Input cleared. The session log was kept. " + READY_STATUS
        )

    def on_accuracy_clicked(self):
        """REQ-11: relative error against the approved dataset."""
        self.write_to_log("--- Accuracy check (approved dataset) ---")
        self.set_status("Running the approved accuracy check...")
        self.root_window.update_idletasks()

        report_lines = check_accuracy()
        failed_count = 0
        for line in report_lines:
            if "[FAIL]" in line:
                failed_count += 1
            self.write_to_log(line, self._tag_for_line(line))

        checked_count = 0
        for _line in report_lines:
            checked_count += 1
        passed_count = checked_count - failed_count
        self.set_status(
            "Accuracy check finished: "
            f"{passed_count} of {checked_count} values within the "
            "1e-6 requirement."
        )


def start_program():
    """Open the calculator window."""
    root_window = tk.Tk()
    GammaWindow(root_window)
    root_window.mainloop()


if __name__ == "__main__":
    start_program()
