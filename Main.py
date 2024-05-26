import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from Widgets import Widgets
from GeometryWindow import GeometryWindow
from CurveSettingsWindow import CurveSettingsWindow
from scipy.interpolate import make_interp_spline
import pandas as pd


def toggle_button_color(button, state):
    """
    Toggle the color of a button based on its state.

    Parameters:
    button (tk.Button): The button to change color.
    state (bool): The state of the button.
    """
    button.config(bg='red' if state else 'SystemButtonFace')


class ImageViewer:
    def __init__(self, _root):
        """
        Initialize the ImageViewer class.

        Parameters:
        root (tk.Tk): The root window of the Tkinter application.
        """
        self.CurveSettingsWindow = CurveSettingsWindow(self)
        self.color = "blue"  # Default color
        self.size = 1
        self.data_table = None
        self.canvas = None
        self.root = _root
        self.root.title("Show Image")
        self.zoom_factor = 1.2

        self.open_image_button = None
        self.image_original = None
        self.image_filtered = None
        self.image_tk = None

        self.axis_button_state = False
        self.set_axis_button_state = False
        self.add_points_button_state = False
        self.calculate_button_state = False

        self.axis_button = None
        self.set_axis_button = None
        self.add_points_button = None
        self.calculate_button = None

        self.axis_state = True
        self.axis_list = []
        self.value_list = []
        self.value_entered = False
        self.axis_counter = 0
        self.selected_axis = None

        self.point_values = []
        self.data_values = []

        self.curves = [[] for _ in range(10)]
        self.current_curve = 1  # Default curve
        self.curve_IDs = [1]
        self.last_ID = 1
        self.curve_names = [f"Curve {i + 1}" for i in range(10)]

        self.history = []
        self.redo_stack = []

        self.Geometry_window = GeometryWindow(self.root, self)
        self.curve_fitting_window = None

        self.checklist = None
        self.grid_lines_visible = False
        self.grid_size_x = 5
        self.grid_size_y = 5

        self.widgets = Widgets(self)
        self.widgets.create_widgets()
        self.root.bind("<Configure>", self.on_resize)

    @staticmethod
    def format_control(file_path):
        """
        Check if the file has a supported image format.

        Parameters:
        file_path (str): The path of the file.

        Returns:
        bool: True if the file has a supported format, False otherwise.
        """
        return file_path.endswith((".jpg", ".jpeg", ".png"))

    def open_image(self):
        """
        Open an image file and display it on the canvas.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                self.image_original = Image.open(file_path)
                if not self.format_control(file_path):
                    messagebox.showerror("Error", "Image format is not supported! Please select a valid image file.")
                    return

                self.image_original = self.image_original.resize((800, 600), Image.Resampling.LANCZOS)
                self.image_tk = ImageTk.PhotoImage(self.image_original)
                self.image_filtered = self.image_original.convert('L').point(lambda x: 0 if x < 128 else 255, '1')

                self.show_image()

            except (IOError, SyntaxError):
                messagebox.showerror("Error", "Image file is not valid! Please select a valid image file.")

    def show_image(self, image_type="original"):
        """
        Display the image on the canvas.

        Parameters:
        image_type (str): The type of image to display ("original" or "filtered").
        """
        self.canvas.delete("all")
        if image_type == "original":
            self.image_tk = ImageTk.PhotoImage(self.image_original)
        elif image_type == "filtered":
            self.image_tk = ImageTk.PhotoImage(self.image_filtered)
        self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, anchor=tk.CENTER,
                                 image=self.image_tk)
        if self.grid_lines_visible:
            self.draw_grid()

    def mouse_click(self, event):
        """
        Handle mouse click events on the canvas.

        Parameters:
        event (tk.Event): The mouse click event.
        """
        if hasattr(self.root, "label"):
            self.root.label.destroy()
        self.root.label = tk.Label(self.root, text=f"X: {event.x}, Y: {event.y}")
        self.root.label.place(x=event.x, y=event.y)
        self.root.label.pack()

    def reset_button_colors(self):
        """
        Reset the color of all toggle buttons.
        """
        buttons = [self.axis_button, self.set_axis_button, self.add_points_button, self.calculate_button]
        for button in buttons:
            toggle_button_color(button, False)

    def show_axis(self):
        """
        Toggle the axis placement mode.
        """
        self.reset_button_colors()
        self.axis_button_state = not self.axis_button_state
        toggle_button_color(self.axis_button, self.axis_button_state)
        if self.axis_button_state:
            self.root.config(cursor="crosshair")
            self.canvas.bind("<Button-1>", self.place_axis)
            self.canvas.bind("<Button-3>", self.delete_axis)
        else:
            self.root.config(cursor="")
            self.canvas.bind("<Button-1>", self.mouse_click)
            self.canvas.bind("<Button-3>", self.select_axis)

    def show_points(self):
        """
        Toggle the points placement mode.
        """
        self.reset_button_colors()
        self.add_points_button_state = not self.add_points_button_state
        toggle_button_color(self.add_points_button, self.add_points_button_state)
        if self.add_points_button_state:
            self.root.config(cursor="dotbox")
            self.canvas.bind("<Button-1>", self.add_points)
            self.canvas.bind("<Button-3>", self.delete_point)
        else:
            self.root.config(cursor="")
            self.canvas.bind("<Button-1>", self.mouse_click)
            self.canvas.bind("<Button-3>", self.select_axis)

    def set_axis(self):
        """
        Set the coordinates for the selected axis.
        """
        self.reset_button_colors()
        self.set_axis_button_state = not self.set_axis_button_state
        toggle_button_color(self.set_axis_button, self.set_axis_button_state)
        if not self.selected_axis:
            messagebox.showinfo("Error", "Please, Select an axis.")
            return

        set_axis_window = tk.Toplevel(self.root)
        set_axis_window.title("Set Axis")

        x_label = tk.Label(set_axis_window, text="New X coordinate:")
        x_label.grid(row=0, column=0, padx=5, pady=5)
        x_entry = tk.Entry(set_axis_window)
        x_entry.grid(row=0, column=1, padx=5, pady=5)

        y_label = tk.Label(set_axis_window, text="New Y coordinate:")
        y_label.grid(row=1, column=0, padx=5, pady=5)
        y_entry = tk.Entry(set_axis_window)
        y_entry.grid(row=1, column=1, padx=5, pady=5)

        confirm_button = tk.Button(set_axis_window, text="Confirm",
                                   command=lambda: self.confirm_axis(set_axis_window, x_entry, y_entry))
        confirm_button.grid(row=2, column=0, columnspan=2, pady=10)

    def confirm_axis(self, window, x_entry, y_entry):
        """
        Confirm the new coordinates for the selected axis.

        Parameters:
        window (tk.Toplevel): The window for setting axis coordinates.
        x_entry (tk.Entry): The entry for the new X coordinate.
        y_entry (tk.Entry): The entry for the new Y coordinate.
        """
        new_x = x_entry.get()
        new_y = y_entry.get()

        if not new_x or not new_y:
            messagebox.showerror("Error", "Please, Enter new X and Y coordinates.")
            return

        try:
            new_x = int(new_x)
            new_y = int(new_y)
        except ValueError:
            messagebox.showerror("Error", "X and Y coordinates must be integer.")
            return

        x, y = self.selected_axis
        for index, axis in enumerate(self.axis_list):
            if axis[0] - 10 <= x <= axis[0] + 10 and axis[1] - 10 <= y <= axis[1] + 10:
                self.axis_list.pop(index)
                self.value_list.pop(index)
                self.axis_counter -= 1
                self.canvas.delete("all")
                self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2,
                                         anchor=tk.CENTER, image=self.image_tk)
                for i, _axis in enumerate(self.axis_list):
                    self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
                    self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
                    self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
                    self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")
        x = new_x
        y = new_y
        self.canvas.create_line(x - 10, y, x + 10, y, fill="red", width=1)
        self.canvas.create_line(x, y - 10, x, y + 10, fill="red", width=1)

        value_text = f"X: {x}, Y: {y}"
        self.canvas.create_text(x, y - 20, text=value_text, fill="blue")
        self.axis_list.append((x, y))
        self.axis_counter += 1
        self.ask_value_for_axis(x, y)
        window.destroy()

    def ask_value_for_axis(self, x, y):
        """
        Ask the user to enter a value for the specified axis coordinates.

        Parameters:
        x (int): The X coordinate of the axis.
        y (int): The Y coordinate of the axis.
        """
        self.value_entered = True

        value_window = tk.Toplevel(self.root)
        value_window.title("Add Value")

        x_label = tk.Label(value_window, text=f"X Coordinate: {x}")
        x_label.grid(row=0, column=0, padx=5, pady=5)

        y_label = tk.Label(value_window, text=f"Y Coordinate: {y}")
        y_label.grid(row=1, column=0, padx=5, pady=5)

        value_x_label = tk.Label(value_window, text="Value for X:")
        value_x_label.grid(row=2, column=0, padx=5, pady=5)
        value_x_entry = tk.Entry(value_window)
        value_x_entry.grid(row=2, column=1, padx=5, pady=5)

        value_y_label = tk.Label(value_window, text="Value for Y:")
        value_y_label.grid(row=3, column=0, padx=5, pady=5)
        value_y_entry = tk.Entry(value_window)
        value_y_entry.grid(row=3, column=1, padx=5, pady=5)

        confirm_button = tk.Button(value_window, text="Add Value", command=lambda: self.add_value_to_axis(
            value_x_entry.get(), value_y_entry.get(), x, y, value_window))
        confirm_button.grid(row=4, column=0, columnspan=2, pady=10)

        value_window.protocol("WM_DELETE_WINDOW", lambda: self.protocol_func(value_window))

    def protocol_func(self, window):
        """
        Handle the window close event for the value entry window.

        Parameters:
        window (tk.Toplevel): The value entry window.
        """
        self.axis_list.pop()
        self.axis_counter -= 1
        self.value_entered = False
        window.destroy()

    def add_value_to_axis(self, value_x, value_y, x, y, value_window):
        """
        Add the specified values to the selected axis.

        Parameters:
        value_x (str): The value for the X coordinate.
        value_y (str): The value for the Y coordinate.
        x (int): The X coordinate of the axis.
        y (int): The Y coordinate of the axis.
        value_window (tk.Toplevel): The window for entering the values.
        """
        if self.check_axis(int(value_x), int(value_y)):
            messagebox.showinfo("Info", "3 points must not be on the same line.")
            return
        if self.is_integer(value_x) and self.is_integer(value_y):
            value_x = int(value_x)
            value_y = int(value_y)
            self.canvas.create_text(x, y + 10, text=f"value X: {value_x}, Y: {value_y}", fill="green")
            self.value_list.append((value_x, value_y))

            value_window.destroy()
        else:
            messagebox.showerror("Error", "Please enter valid integer values for X and Y.")
        self.value_entered = False

    @staticmethod
    def is_integer(s):
        """
        Check if the given string is an integer.

        Parameters:
        s (str): The string to check.

        Returns:
        bool: True if the string is an integer, False otherwise.
        """
        try:
            int(s)
            return True
        except ValueError:
            return False

    def add_points(self, event):
        """
        Add a point to the current curve.

        Parameters:
        event (tk.Event): The mouse click event.
        """
        if self.axis_counter < 3:
            messagebox.showinfo("Info", "Please, Add at least 3 axis to add points.")
            return
        x, y = event.x, event.y
        self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="blue")
        point_text = f"X: {x}, Y: {y}"
        self.canvas.create_text(x, y - 20, text=point_text, fill="purple")
        self.curves[self.current_curve - 1].append((x, y))
        self.draw_curve_line()

    def draw_curve_line(self):
        """
        Draw the curve line based on the points added to the current curve.
        """
        self.redraw_canvas(1)

        x_list = [self.curves[self.current_curve - 1][i][0] for i in range(len(self.curves[self.current_curve - 1]))]
        y_list = [self.curves[self.current_curve - 1][i][1] for i in range(len(self.curves[self.current_curve - 1]))]

        if len(x_list) < 2:
            return

        x_list = np.array(x_list)
        y_list = np.array(y_list)

        sorted_indices = np.argsort(x_list)
        x_list = x_list[sorted_indices]
        y_list = y_list[sorted_indices]

        if len(x_list) < 4:
            for i in range(len(x_list) - 1):
                x1, y1 = x_list[i], y_list[i]
                x2, y2 = x_list[i + 1], y_list[i + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=self.size)
        else:
            x_array = np.array(x_list)
            y_array = np.array(y_list)

            try:
                x_list2 = []
                y_list2 = []
                split_index = -1
                for i in range(len(x_array) - 1):
                    if abs(x_array[i] - x_array[i + 1]) <= 2:
                        split_index = i + 1
                        break
                if split_index != -1:
                    x_list1 = np.array(x_array[:split_index])
                    y_list1 = np.array(y_array[:split_index])
                    x_list2 = np.array(x_array[split_index:])
                    y_list2 = np.array(y_array[split_index:])
                else:
                    x_list1 = np.array(x_array)
                    y_list1 = np.array(y_array)
                x_new = np.linspace(x_list1.min(), x_list1.max(), 100)
                y_new = make_interp_spline(x_list1, y_list1, k=2)(x_new)
                for i in range(len(x_new) - 1):
                    x1, y1 = x_new[i], y_new[i]
                    x2, y2 = x_new[i + 1], y_new[i + 1]
                    self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=self.size)

                if len(x_list2) == 0:
                    return

                self.canvas.create_line(x_list1[-1], y_list1[-1], x_list2[0], y_list2[0], fill=self.color,
                                        width=self.size, dash=(4, 4))

                if len(x_list2) < 4:
                    for i in range(len(x_list2) - 1):
                        x1, y1 = x_list2[i], y_list2[i]
                        x2, y2 = x_list2[i + 1], y_list2[i + 1]
                        self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=self.size)
                else:
                    x_new = np.linspace(x_list2.min(), x_list2.max(), 100)
                    y_new = make_interp_spline(x_list2, y_list2, k=2)(x_new)
                    for i in range(len(x_new) - 1):
                        x1, y1 = x_new[i], y_new[i]
                        x2, y2 = x_new[i + 1], y_new[i + 1]
                        self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=self.size)

            except ValueError as e:
                return

    def switch_curve(self):
        """
        Switch to a different curve.
        """
        switch_curve_window = tk.Toplevel(self.root)
        switch_curve_window.title("Switch Curve")
        # Create a listbox to show the curves
        listbox = tk.Listbox(switch_curve_window, selectmode=tk.SINGLE)
        for curve in self.curve_IDs:
            listbox.insert(tk.END, self.curve_names[curve - 1])
        listbox.pack()

        switch_button = tk.Button(switch_curve_window, text="Switch",
                                  command=lambda: self.switch_curve_cont(
                                      self.curve_IDs[self.curve_names.index(listbox.get(listbox.curselection()))]))
        switch_button.pack()

    def switch_curve_cont(self, curve):
        """
        Continue switching to the selected curve.

        Parameters:
        curve (int): The ID of the selected curve.
        """
        self.current_curve = curve
        self.widgets.set_current_curve(self.curve_names[curve - 1])
        self.canvas.delete("all")
        self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, anchor=tk.CENTER,
                                 image=self.image_tk)
        try:
            self.redraw_canvas()
        except IndexError:
            for i, _axis in enumerate(self.axis_list):
                self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
                self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
                self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
                self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")

    def add_curve(self):
        """
        Add a new curve to the list.
        """
        if self.last_ID == 10:
            messagebox.showinfo("Info", "You can not add more than 10 curves.")
            return
        self.last_ID += 1
        self.curve_IDs.append(self.last_ID)

    def delete_curve(self):
        """
        Delete the current curve.
        """
        if len(self.curve_IDs) == 1:
            messagebox.showinfo("Info", "You can not delete the last curve.")
            return
        self.curve_IDs.pop(self.current_curve - 1)
        self.last_ID -= 1
        for index, i in enumerate(self.curve_IDs):
            if i > self.current_curve:
                self.curve_IDs[index] -= 1

        self.curves[self.current_curve - 1] = []
        if self.current_curve == 1:
            self.switch_curve_cont(2)
        else:
            self.switch_curve_cont(self.current_curve - 1)

    def place_axis(self, event):
        """
        Place an axis at the specified coordinates.

        Parameters:
        event (tk.Event): The mouse click event.
        """
        if self.value_entered:
            messagebox.showinfo("Info", "Please, Enter the value for the previous axis.")
            return
        if self.axis_counter == 3:
            messagebox.showinfo("Info", "You can only add 3 axes.")
            return

        x, y = float(event.x), float(event.y)
        self.canvas.create_line(x - 10, y, x + 10, y, fill="red", width=1)
        self.canvas.create_line(x, y - 10, x, y + 10, fill="red", width=1)

        value_text = f"X: {x}, Y: {y}"
        self.canvas.create_text(x, y - 20, text=value_text, fill="blue")
        self.axis_list.append((x, y))
        self.axis_counter += 1
        self.ask_value_for_axis(x, y)

    def delete_axis(self, event):
        """
        Delete the axis at the specified coordinates.

        Parameters:
        event (tk.Event): The mouse click event.
        """
        if self.value_entered:
            messagebox.showinfo("Info", "Please, Enter the value for the previous axis.")
            return

        x, y = event.x, event.y
        for index, axis in enumerate(self.axis_list):
            if axis[0] - 10 <= x <= axis[0] + 10 and axis[1] - 10 <= y <= axis[1] + 10:
                self.axis_list.pop(index)
                self.value_list.pop(index)
                self.axis_counter -= 1
                self.canvas.delete("all")
                self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2,
                                         anchor=tk.CENTER, image=self.image_tk)
                self.redraw_canvas()

    def select_axis(self, event):
        """
        Select an axis at the specified coordinates.

        Parameters:
        event (tk.Event): The mouse click event.
        """
        x, y = event.x, event.y
        for index, axis in enumerate(self.axis_list):
            if axis[0] - 10 <= x <= axis[0] + 10 and axis[1] - 10 <= y <= axis[1] + 10:
                self.selected_axis = axis
                self.widgets.set_selected_axis(axis)
                break

    def check_axis(self, value_x, value_y) -> bool:
        """
        Check if three points are collinear.

        Parameters:
        value_x (int): The X coordinate of the third point.
        value_y (int): The Y coordinate of the third point.

        Returns:
        bool: True if the points are collinear, False otherwise.
        """
        if self.axis_counter < 3:
            return False
        axis1 = self.value_list[0]
        axis2 = self.value_list[1]
        axis3 = [value_x, value_y]

        if (axis1[0] * (axis2[1] - axis3[1]) + axis2[0] * (axis3[1] - axis1[1]) + axis3[0] * (
                axis1[1] - axis2[1])) == 0:
            return True

    def delete_point(self, event):
        """
        Delete a point from the current curve.

        Parameters:
        event (tk.Event): The mouse click event.
        """
        x, y = event.x, event.y
        for index, point in enumerate(self.curves[self.current_curve - 1]):
            if point[0] - 2 <= x <= point[0] + 2 and point[1] - 2 <= y <= point[1] + 2:
                self.curves[self.current_curve - 1].pop(index)
                self.canvas.delete("all")
                self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2,
                                         anchor=tk.CENTER, image=self.image_tk)
                self.redraw_canvas()

    def calculate_values(self):
        """
        Calculate values for the points on the curves.
        """
        try:
            self.data_values.clear()
            self.reset_button_colors()
            self.calculate_button_state = not self.calculate_button_state
            toggle_button_color(self.calculate_button, self.calculate_button_state)

            axis1 = self.axis_list[0]
            axis2 = self.axis_list[1]
            axis3 = self.axis_list[2]

            value1 = self.value_list[0]
            value2 = self.value_list[1]
            value3 = self.value_list[2]

            curves = self.curves

            x_list = [axis1[0], axis2[0], axis3[0]]
            y_list = [axis1[1], axis2[1], axis3[1]]

            x_value_list = [value1[0], value2[0], value3[0]]
            y_value_list = [value1[1], value2[1], value3[1]]

            x_min = min(x_list)
            x_max = max(x_list)

            x_value_min = min(x_value_list)
            x_value_max = max(x_value_list)

            x_diff = abs(x_max) - abs(x_min)
            x_value_diff = x_value_max - x_value_min

            x_ratio = x_diff / x_value_diff

            for i, curve in enumerate(curves):
                for point in curve:
                    x = point[0]
                    y = point[1]

                    x_value = (x - x_min) / x_ratio
                    coeffs = np.polyfit(y_list, y_value_list, 1)
                    y_value = coeffs[0] * y + coeffs[1]

                    self.point_values.append((x_value, y_value))
                if not self.curves[i]:
                    continue
                else:
                    values = []
                    for j, point in enumerate(self.point_values):
                        values.append([float(f"{point[0]:.2f}"), float(f"{point[1]:.2f}")])
                    self.data_values.append(values)
                    self.point_values.clear()
            self.data_table = self.create_data_table()

            self.Geometry_window.populate_tree()
            self.widgets.toggle_geometry_window()
            self.widgets.toggle_geometry_window()
        except IndexError:
            messagebox.showinfo("Info", "Please, Add 3 axis and at least 1 point to calculate values.")
            return

    def clear_canvas(self):
        """
        Clear all drawings from the canvas.
        """
        self.canvas.delete("all")
        if self.image_tk:
            self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, anchor=tk.CENTER,
                                     image=self.image_tk)
        if self.grid_lines_visible:
            self.draw_grid()

    def redraw_canvas(self, n=0):
        """
        Redraw all elements on the canvas.

        Parameters:
        n (int): Flag to indicate additional elements to draw.
        """
        self.clear_canvas()
        if n == 0:
            for i, _axis in enumerate(self.axis_list):
                self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
                self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
                self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
                self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")
            for i, _point in enumerate(self.curves[self.current_curve - 1]):
                self.canvas.create_oval(_point[0] - 2, _point[1] - 2, _point[0] + 2, _point[1] + 2, fill="blue")
                point_text = f"X: {_point[0]}, Y: {_point[1]}"
                self.canvas.create_text(_point[0], _point[1] - 20, text=point_text, fill="purple")
            self.draw_curve_line()
        if n == 1:
            for i, _axis in enumerate(self.axis_list):
                self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
                self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
                self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
                self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")
            for i, _point in enumerate(self.curves[self.current_curve - 1]):
                self.canvas.create_oval(_point[0] - 2, _point[1] - 2, _point[0] + 2, _point[1] + 2, fill="blue")
                point_text = f"X: {_point[0]}, Y: {_point[1]}"
                self.canvas.create_text(_point[0], _point[1] - 20, text=point_text, fill="purple")

    def toggle_geometry_window(self):
        """
        Toggle the visibility of the Geometry Window.
        """
        if self.Geometry_window:
            self.widgets.paned_window.forget(self.Geometry_window.frame)
            self.Geometry_window = None
        else:
            self.Geometry_window = GeometryWindow(self.widgets.paned_window, self)
            self.widgets.paned_window.add(self.Geometry_window.frame)

    def show_original_image(self):
        """
        Display the original image on the canvas.
        """
        self.show_image("original")

    def show_filtered_image(self):
        """
        Display the filtered image on the canvas.
        """
        self.show_image("filtered")

    def hide_image(self):
        """
        Hide the image from the canvas.
        """
        self.canvas.delete("all")

    def draw_grid(self):
        """
        Draw grid lines on the canvas.
        """
        self.canvas.delete('grid_line')
        if not self.image_tk:
            return
        image_width = self.image_tk.width()
        image_height = self.image_tk.height()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x_offset = (canvas_width - image_width) // 2
        y_offset = (canvas_height - image_height) // 2
        for i in range(0, image_width, image_width // int(self.grid_size_x)):
            self.canvas.create_line([(i + x_offset, y_offset), (i + x_offset, y_offset + image_height)],
                                    tag='grid_line', fill='gray')
        for i in range(0, image_height, image_height // int(self.grid_size_y)):
            self.canvas.create_line([(x_offset, i + y_offset), (x_offset + image_width, i + y_offset)], tag='grid_line',
                                    fill='gray')

    def on_resize(self, event):
        """
        Handle window resize events.

        Parameters:
        event (tk.Event): The resize event.
        """
        self.canvas.config(width=event.width, height=event.height)
        self.redraw_canvas()

    def create_data_table(self):
        """
        Create a data table from the calculated values.

        Returns:
        pd.DataFrame: The data table.
        """
        data = []
        for i, curve in enumerate(self.data_values):
            for j, point in enumerate(curve):
                data.append([i + 1, f"point {j + 1}", point[0], point[1]])

        data_table = pd.DataFrame(data, columns=["Curve", "Point", "X", "Y"])
        return data_table

    def export_data(self):
        """
        Export the data table to a CSV file.
        """
        if self.data_table is None:
            messagebox.showinfo("Info", "Please, Calculate values to export data.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.data_table.to_csv(file_path, index=False)


if __name__ == "__main__":
    root = tk.Tk()
    image_viewer = ImageViewer(root)
    root.mainloop()
