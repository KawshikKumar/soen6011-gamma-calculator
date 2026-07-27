"""
Tkinter front end for the from-scratch Gamma calculator (D2/Problem 5).

Single input box on the left accepts one or more lines: a plain
argument (REQ-05/06) or "argument, expected_value" to check against a
value Cooper already trusts (REQ-14 for one line, REQ-15 for several).
The session log sits on the right so results build up next to the
input instead of underneath it.

Run this file to start the program:
    python gamma_gui.py
"""

import tkinter as tk
from tkinter import ttk

from gamma_exceptions import GammaInputProblem
from gamma_core import (
    evaluate_lines,
    check_accuracy,
)

# A quiet, low-contrast palette - a plain dark editor look rather than
# a bright theme, so the numbers are what stands out, not the colors.
BACKDROP = "#21242b"        # window background
PANEL_SHADE = "#2a2e37"     # input box / log background
LINE_EDGE = "#3a3f4b"       # subtle borders
TEXT_PRIMARY = "#e4e6eb"    # normal readable text
TEXT_MUTED = "#888c96"      # secondary / hint text
ACCENT = "#6fa8c9"          # single muted accent, used sparingly
GOOD_SIGNAL = "#7fae7f"     # PASS lines, muted green
BAD_SIGNAL = "#c07d7d"      # FAIL / error lines, muted red

INPUT_HINT_TEXT = (
    "4.5\n"
    "5, 24\n"
    "0.5, 1.772454"
)


class GammaWindow:
    """Holds every widget for the calculator window."""

    def __init__(self, root_window):
        self.root_window = root_window
        root_window.title("Galaxy Gamma Calculator")
        root_window.configure(background=BACKDROP)
        root_window.geometry("760x520")
        root_window.minsize(680, 460)

        self._build_style()
        self._build_layout()

    # ------------------------------------------------------------------
    # Look and feel
    # ------------------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self.root_window)
        style.theme_use("clam")

        style.configure("Sky.TFrame", background=BACKDROP)
        style.configure("Panel.TFrame", background=PANEL_SHADE)

        style.configure(
            "Title.TLabel", background=BACKDROP, foreground=TEXT_PRIMARY,
            font=("Segoe UI", 15, "bold"),
        )
        style.configure(
            "Subtitle.TLabel", background=BACKDROP, foreground=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Field.TLabel", background=BACKDROP, foreground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Hint.TLabel", background=BACKDROP, foreground=TEXT_MUTED,
            font=("Segoe UI", 8),
        )
        style.configure(
            "SectionHeading.TLabel", background=BACKDROP, foreground=TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "Primary.TButton", background=ACCENT, foreground=BACKDROP,
            font=("Segoe UI", 10, "bold"), padding=8, borderwidth=0,
        )
        style.map("Primary.TButton", background=[("active", "#89bcd9")])

        style.configure(
            "Quiet.TButton", background=PANEL_SHADE, foreground=TEXT_PRIMARY,
            font=("Segoe UI", 9), padding=6, borderwidth=0,
        )
        style.map("Quiet.TButton", background=[("active", "#343945")])

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        self.root_window.columnconfigure(0, weight=1, uniform="half")
        self.root_window.columnconfigure(1, weight=1, uniform="half")
        self.root_window.rowconfigure(0, weight=1)

        left_column = ttk.Frame(self.root_window, style="Sky.TFrame", padding=18)
        left_column.grid(row=0, column=0, sticky="nsew")

        right_column = ttk.Frame(self.root_window, style="Sky.TFrame", padding=(0, 18, 18, 18))
        right_column.grid(row=0, column=1, sticky="nsew")

        self._build_input_panel(left_column)
        self._build_log_panel(right_column)

    def _build_input_panel(self, parent):
        ttk.Label(parent, text="Galaxy Gamma Calculator", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            parent,
            text="Gamma-function checks for galaxy-luminosity research (Lanczos, from scratch)",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 16))

        ttk.Label(parent, text="Enter one or more lines:", style="Field.TLabel").pack(anchor="w")
        ttk.Label(
            parent,
            text="A single number to calculate, or 'argument, expected_value' to verify it.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(0, 6))

        input_frame = ttk.Frame(parent, style="Panel.TFrame", padding=2)
        input_frame.pack(fill="x")
        self.input_box = tk.Text(
            input_frame, height=8, wrap="none",
            background=PANEL_SHADE, foreground=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, borderwidth=0,
            highlightthickness=1, highlightbackground=LINE_EDGE,
            font=("Consolas", 11), padx=8, pady=8,
        )
        self.input_box.pack(fill="x")
        self.input_box.insert("1.0", INPUT_HINT_TEXT)

        button_row = ttk.Frame(parent, style="Sky.TFrame")
        button_row.pack(fill="x", pady=12)

        ttk.Button(
            button_row, text="Calculate", style="Primary.TButton",
            command=self.on_calculate_clicked,
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            button_row, text="Clear", style="Quiet.TButton",
            command=self.on_clear_clicked,
        ).pack(side="left")

        ttk.Label(parent, text="", style="Field.TLabel").pack(pady=4)  # small spacer

        ttk.Separator(parent).pack(fill="x", pady=(4, 12))

        ttk.Label(
            parent, text="Approved test dataset (REQ-11)", style="SectionHeading.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            parent,
            text="A fixed set of known-correct values, unrelated to what you type above.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(0, 8))
        ttk.Button(
            parent, text="Run accuracy check", style="Quiet.TButton",
            command=self.on_accuracy_clicked,
        ).pack(anchor="w")

    def _build_log_panel(self, parent):
        ttk.Label(parent, text="Session log", style="SectionHeading.TLabel").pack(anchor="w")
        ttk.Label(
            parent, text="Every calculation and check you run appears here.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(0, 6))

        log_frame = ttk.Frame(parent, style="Panel.TFrame", padding=2)
        log_frame.pack(fill="both", expand=True)

        self.log_box = tk.Text(
            log_frame, wrap="word", state="disabled",
            background=PANEL_SHADE, foreground=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, borderwidth=0,
            highlightthickness=1, highlightbackground=LINE_EDGE,
            font=("Consolas", 10), padx=10, pady=10,
        )
        self.log_box.pack(fill="both", expand=True)
        self.log_box.tag_configure("good_line", foreground=GOOD_SIGNAL)
        self.log_box.tag_configure("bad_line", foreground=BAD_SIGNAL)
        self.log_box.tag_configure("normal_line", foreground=TEXT_PRIMARY)

    # ------------------------------------------------------------------
    # Behaviour
    # ------------------------------------------------------------------
    def write_to_log(self, message_line, tag_name="normal_line"):
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

    def on_calculate_clicked(self):
        """
        REQ-05/06/10: shows argument+result together, allows repeats,
        keeps running after invalid input - now per line, not just per
        session, so one bad line does not hide the good ones around it.
        Also covers REQ-14 (one compare line) and REQ-15 (several
        compare lines) through the same box, depending on what the
        user typed.
        """
        raw_text = self.input_box.get("1.0", "end")
        self.write_to_log("--- Calculate ---")
        try:
            line_results = evaluate_lines(raw_text)
        except GammaInputProblem as input_error:
            # Only raised when there was nothing usable to evaluate at all.
            self.write_to_log(f"Input error: {input_error}", "bad_line")
            return

        pass_count = 0
        checked_count = 0
        error_count = 0

        for line_number, message, status in line_results:
            if status == "error":
                error_count += 1
                self.write_to_log(message, "bad_line")
            elif status == "pass":
                pass_count += 1
                checked_count += 1
                self.write_to_log(message, "good_line")
            elif status == "fail":
                checked_count += 1
                self.write_to_log(message, "bad_line")
            else:
                self.write_to_log(message, "normal_line")

        summary_parts = []
        if checked_count:
            summary_parts.append(f"{pass_count} of {checked_count} checks passed")
        if error_count:
            summary_parts.append(f"{error_count} line(s) had errors")
        if summary_parts:
            self.write_to_log("Summary: " + "; ".join(summary_parts) + ".")

    def on_clear_clicked(self):
        """Empty the input box for a fresh set of lines."""
        self.input_box.delete("1.0", "end")
        self.input_box.focus()

    def on_accuracy_clicked(self):
        """REQ-11: show relative error against the fixed, approved test dataset."""
        self.write_to_log("--- Accuracy check (approved dataset) ---")
        for line in check_accuracy():
            self.write_to_log(line, self._tag_for_line(line))


def start_program():
    root_window = tk.Tk()
    GammaWindow(root_window)
    root_window.mainloop()


if __name__ == "__main__":
    start_program()