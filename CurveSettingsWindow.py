import tkinter as tk
from tkinter import colorchooser


class CurveSettingsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.settings_window = None

    def open_settings_window(self):
        if self.settings_window is not None:
            self.settings_window.destroy()

        self.settings_window = tk.Toplevel(self.parent.root)
        self.settings_window.title("Curve Settings")

        color_label = tk.Label(self.settings_window, text="Select Curve Color:")
        color_label.grid(row=0, column=0, padx=5, pady=5)

        color_button = tk.Button(self.settings_window, text="Choose Color", command=self.choose_color)
        color_button.grid(row=0, column=1, padx=5, pady=5)

        size_label = tk.Label(self.settings_window, text="Set Curve Size:")
        size_label.grid(row=1, column=0, padx=5, pady=5)

        size_label = tk.Scale(self.settings_window, from_=1, to=3, orient=tk.HORIZONTAL, command=self.change_size)
        size_label.set(self.parent.size)
        size_label.grid(row=1, column=1, padx=5, pady=5)

        apply_button = tk.Button(self.settings_window, text="Apply", command=self.apply_settings)
        apply_button.grid(row=3, column=0, columnspan=2, pady=10)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code:
            self.parent.color = color_code

    def change_size(self, value):
        self.parent.size = value

    def apply_settings(self):
        self.parent.draw_curve_line()
        self.settings_window.destroy()
