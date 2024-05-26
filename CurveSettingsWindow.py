import tkinter as tk
from tkinter import colorchooser


class CurveSettingsWindow:
    def __init__(self, parent):
        """
        Initialize the CurveSettingsWindow class.

        Parameters:
        parent (tk.Widget): The parent widget that contains the settings.
        """
        self.parent = parent
        self.settings_window = None

    def open_settings_window(self):
        """
        Open a new window for curve settings. If a settings window is already open, it will be destroyed and recreated.
        """
        if self.settings_window is not None:
            self.settings_window.destroy()

        self.settings_window = tk.Toplevel(self.parent.root)
        self.settings_window.title("Curve Settings")

        # Label for curve color selection
        color_label = tk.Label(self.settings_window, text="Select Curve Color:")
        color_label.grid(row=0, column=0, padx=5, pady=5)

        # Button to open color chooser
        color_button = tk.Button(self.settings_window, text="Choose Color", command=self.choose_color)
        color_button.grid(row=0, column=1, padx=5, pady=5)

        # Label for curve size setting
        size_label = tk.Label(self.settings_window, text="Set Curve Size:")
        size_label.grid(row=1, column=0, padx=5, pady=5)

        # Scale for adjusting curve size
        size_scale = tk.Scale(self.settings_window, from_=1, to=3, orient=tk.HORIZONTAL, command=self.change_size)
        size_scale.set(self.parent.size)
        size_scale.grid(row=1, column=1, padx=5, pady=5)

        # Button to apply settings
        apply_button = tk.Button(self.settings_window, text="Apply", command=self.apply_settings)
        apply_button.grid(row=3, column=0, columnspan=2, pady=10)

    def choose_color(self):
        """
        Open a color chooser dialog to select a color. Sets the selected color to the parent's color attribute.
        """
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code:
            self.parent.color = color_code

    def change_size(self, value):
        """
        Change the size of the curve based on the scale value.

        Parameters:
        value (int): The new size value.
        """
        self.parent.size = value

    def apply_settings(self):
        """
        Apply the selected settings and redraw the curve line. Closes the settings window.
        """
        self.parent.draw_curve_line()
        self.settings_window.destroy()
