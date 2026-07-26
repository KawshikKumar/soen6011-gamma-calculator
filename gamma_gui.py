"""
Tkinter front end for the from-scratch Gamma calculator (D2/Problem 5).

Run this file to start the program:
    python gamma_gui.py
"""

import tkinter as tk
from tkinter import ttk

from gamma_exceptions import GammaInputProblem, GammaRangeProblem
from gamma_core import (
    read_positive_argument,
    gamma_from_scratch,
    format_with_digits,
    check_accuracy,
)


class GammaWindow:
    """Holds every widget for the single-window calculator."""

    def __init__(self, root_window):
        self.root_window = root_window
        root_window.title("Gamma Function Calculator (from scratch)")

        instruction_label = ttk.Label(
            root_window,
            text="Enter a positive real argument (example: 4.5 or 2e-3):",
        )
        instruction_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 2), sticky="w")

        self.entry_box = ttk.Entry(root_window, width=25)
        self.entry_box.grid(row=1, column=0, padx=10, pady=5, sticky="we")
        self.entry_box.bind("<Return>", lambda event: self.on_calculate_clicked())
        self.entry_box.focus()

        calculate_button = ttk.Button(root_window, text="Calculate", command=self.on_calculate_clicked)
        calculate_button.grid(row=1, column=1, padx=10, pady=5)

        self.result_text = tk.StringVar(value="Result will appear here.")
        result_label = ttk.Label(root_window, textvariable=self.result_text, wraplength=320)
        result_label.grid(row=2, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

        accuracy_button = ttk.Button(
            root_window, text="Run accuracy check", command=self.on_accuracy_clicked
        )
        accuracy_button.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10))

        history_label = ttk.Label(root_window, text="History / accuracy log:")
        history_label.grid(row=4, column=0, columnspan=2, padx=10, sticky="w")

        self.log_box = tk.Text(root_window, height=10, width=45, state="disabled")
        self.log_box.grid(row=5, column=0, columnspan=2, padx=10, pady=(0, 10))

    def write_to_log(self, message_line):
        """Add one line of text to the scrolling history box."""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message_line + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def on_calculate_clicked(self):
        """REQ-05/06/10: show argument+result together, allow repeats, keep running."""
        raw_text = self.entry_box.get()
        try:
            argument_value = read_positive_argument(raw_text)
            gamma_value = gamma_from_scratch(argument_value)
        except GammaInputProblem as input_error:
            self.result_text.set(f"Input error: {input_error}")
        except GammaRangeProblem as range_error:
            self.result_text.set(f"Calculation error: {range_error}")
        else:
            shown_argument = format_with_digits(argument_value)
            shown_result = format_with_digits(gamma_value)
            message = f"Gamma({shown_argument}) = {shown_result}"
            self.result_text.set(message)
            self.write_to_log(message)

    def on_accuracy_clicked(self):
        """REQ-11: show relative error against the approved test dataset."""
        self.write_to_log("--- Accuracy check ---")
        for line in check_accuracy():
            self.write_to_log(line)


def start_program():
    root_window = tk.Tk()
    GammaWindow(root_window)
    root_window.mainloop()


if __name__ == "__main__":
    start_program()
