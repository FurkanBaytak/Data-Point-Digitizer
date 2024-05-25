import tkinter as tk
from tkinter import colorchooser


class GridSettings:
    def __init__(self, parent):
        self.parent = parent
        self.settings_window = None

    def open_settings_window(self):
        if self.settings_window is not None:
            self.settings_window.destroy()

        self.settings_window = tk.Toplevel(self.parent.root)
        self.settings_window.title("Grid Settings")

        size_label_x = tk.Label(self.settings_window, text="Set Grid Size X:")
        size_label_x.grid(row=1, column=0, padx=5, pady=5)
        size_label_x = tk.Scale(self.settings_window, from_=1, to=12, orient=tk.HORIZONTAL, command=self.change_size_x)
        size_label_x.set(self.parent.grid_size_x)
        size_label_x.grid(row=1, column=1, padx=5, pady=5)

        size_label_y = tk.Label(self.settings_window, text="Set Grid Size Y:")
        size_label_y.grid(row=2, column=0, padx=5, pady=5)
        size_label_y = tk.Scale(self.settings_window, from_=1, to=12, orient=tk.HORIZONTAL, command=self.change_size_y)
        size_label_y.set(self.parent.grid_size_y)
        size_label_y.grid(row=2, column=1, padx=5, pady=5)

        apply_button = tk.Button(self.settings_window, text="Apply", command=self.apply_settings)
        apply_button.grid(row=3, column=0, columnspan=2, pady=10)

    def change_size_x(self, value):
        self.parent.grid_size_x = value

    def change_size_y(self, value):
        self.parent.grid_size_y = value

    def apply_settings(self):
        self.parent.draw_grid()
        self.settings_window.destroy()