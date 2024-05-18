import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
from Widgets import Widgets
from GeometryWindow import GeometryWindow
from CurveFittingWindow import CurveFittingWindow

def toggle_button_color(button, state):
    button.config(bg='red' if state else 'SystemButtonFace')

class ImageViewer:
    def __init__(self, _root):
        self.show_all_curves_var = None
        self.show_selected_curve_var = None
        self.hide_all_curves_var = None
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

        self.points = []
        self.point_values = []

        self.curves = [[], [], [], [], [], [], [], [], [], []]
        self.current_curve = 1  # Default curve
        self.curve_IDs = [1]
        self.last_ID = 1

        self.history = []
        self.redo_stack = []

        self.geometry_window = None
        self.curve_fitting_window = None

        self.checklist = None

        self.widgets = Widgets(self)
        self.widgets.create_widgets()
        self.root.bind("<Configure>", self.on_resize)

    @staticmethod
    def format_control(file_path):
        return file_path.endswith((".jpg", ".jpeg", ".png"))

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                self.image_original = Image.open(file_path)
                if not self.format_control(file_path):
                    raise messagebox.showerror("Error", "Image format is not supported! Please select a valid image file.")
                self.image_original = self.image_original.resize((800, 600), Image.Resampling.LANCZOS)
                self.image_tk = ImageTk.PhotoImage(self.image_original)
                self.image_filtered = self.image_original.convert('L').point(lambda x: 0 if x < 128 else 255, '1')

                self.show_image()

            except (IOError, SyntaxError):
                raise messagebox.showerror("Error", "Image file is not valid! Please select a valid image file.")

    def show_image(self, image_type="original"):
        self.canvas.delete("all")
        if image_type == "original":
            self.image_tk = ImageTk.PhotoImage(self.image_original)
        elif image_type == "filtered":
            self.image_tk = ImageTk.PhotoImage(self.image_filtered)
        self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, anchor=tk.CENTER, image=self.image_tk)
        self.draw_grid()

    def mouse_click(self, event):
        if hasattr(self.root, "label"):
            self.root.label.destroy()
        self.root.label = tk.Label(self.root, text=f"X: {event.x}, Y: {event.y}")
        self.root.label.place(x=event.x, y=event.y)
        self.root.label.pack()

    def reset_button_colors(self):
        buttons = [self.axis_button, self.set_axis_button, self.add_points_button, self.calculate_button]
        for button in buttons:
            toggle_button_color(button, False)

    def show_axis(self):
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

        confirm_button = tk.Button(set_axis_window, text="Confirm", command=lambda: self.confirm_axis(set_axis_window, x_entry, y_entry))
        confirm_button.grid(row=2, column=0, columnspan=2, pady=10)

    def confirm_axis(self, window, x_entry, y_entry):
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

        x = self.selected_axis[0]
        y = self.selected_axis[1]
        for index, axis in enumerate(self.axis_list):
            if axis[0] - 10 <= x <= axis[0] + 10 and axis[1] - 10 <= y <= axis[1] + 10:
                self.axis_list.pop(index)
                self.value_list.pop(index)
                self.axis_counter -= 1
                self.save_state()  # Save state after deleting an axis
                self.canvas.delete("all")
                self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, anchor=tk.CENTER, image=self.image_tk)
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
        self.save_state()  # Save state after adding a new axis
        self.ask_value_for_axis(x, y)
        window.destroy()

    def ask_value_for_axis(self, x, y):
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

        confirm_button = tk.Button(value_window, text="Add Value", command=lambda: self.add_value_to_axis(value_x_entry.get(), value_y_entry.get(), x, y, value_window))
        confirm_button.grid(row=4, column=0, columnspan=2, pady=10)

    def add_value_to_axis(self, value_x, value_y, x, y, value_window):
        if value_x.isdigit() and value_y.isdigit():
            value_x = int(value_x)
            value_y = int(value_y)
            self.canvas.create_text(x, y + 10, text=f"value X: {value_x}, Y: {value_y}", fill="green")
            self.value_list.append((value_x, value_y))
            value_window.destroy()
            self.save_state()  # Save state after adding value
        else:
            messagebox.showerror("Error", "Please, Enter valid values for X and Y.")
        self.value_entered = False

    def add_points(self, event):
        if self.axis_counter < 3:
            messagebox.showinfo("Info", "Please, Add at least 3 axis to add points.")
            return
        x, y = event.x, event.y
        self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="blue")
        point_text = f"X: {x}, Y: {y}"
        self.canvas.create_text(x, y - 20, text=point_text, fill="purple")
        self.curves[self.current_curve-1].append((x, y))
        self.save_state()  # Save state after adding points

    def switch_curve(self):
        switch_curve_window = tk.Toplevel(self.root)
        switch_curve_window.title("Switch Curve")
        # Create a listbox to show the curves
        listbox = tk.Listbox(switch_curve_window, selectmode=tk.SINGLE)
        for curve in self.curve_IDs:
            listbox.insert(tk.END, f"Curve {curve}")
        listbox.pack()

        switch_button = tk.Button(switch_curve_window, text="Switch", command=lambda: self.switch_curve_cont(int(listbox.get(tk.ACTIVE).split()[1])))
        switch_button.pack()

    def switch_curve_cont(self, curve):
        self.current_curve = curve
        self.widgets.set_current_curve(self.current_curve)
        self.canvas.delete("all")
        self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, anchor=tk.CENTER, image=self.image_tk)
        try:
            for point in self.curves[curve-1]:
                x, y = point
                self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="blue")
                point_text = f"X: {x}, Y: {y}"
                self.canvas.create_text(x, y - 20, text=point_text, fill="purple")
            for i, _axis in enumerate(self.axis_list):
                self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
                self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
                self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
                self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")
        except IndexError:
            print("Index Error")
            for i, _axis in enumerate(self.axis_list):
                self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
                self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
                self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
                self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")

    def add_curve(self):
        self.last_ID += 1
        self.curve_IDs.append(self.last_ID)
        self.save_state()  # Save state after adding a curve

    def delete_curve(self):
        if len(self.curve_IDs) == 1:
            messagebox.showinfo("Info", "You can not delete the last curve.")
            return
        self.curve_IDs.pop(self.current_curve-1)
        for index, i in enumerate(self.curve_IDs):
            if i > self.current_curve:
                self.curve_IDs[index] -= 1

        self.curves.pop(self.current_curve-1)
        if self.current_curve == 1:
            self.switch_curve_cont(2)
        else:
            self.switch_curve_cont(self.current_curve-1)
        self.save_state()  # Save state after deleting a curve

    def place_axis(self, event):
        if self.value_entered:
            messagebox.showinfo("Info", "Please, Enter the value for the previous axis.")
            return
        if self.axis_counter == 3:
            messagebox.showinfo("Info", "You can only add 4 axes.")
            return

        x, y = float(event.x), float(event.y)
        self.canvas.create_line(x - 10, y, x + 10, y, fill="red", width=1)
        self.canvas.create_line(x, y - 10, x, y + 10, fill="red", width=1)

        value_text = f"X: {x}, Y: {y}"
        self.canvas.create_text(x, y - 20, text=value_text, fill="blue")
        self.axis_list.append((x, y))
        self.axis_counter += 1
        self.save_state()  # Save state after placing an axis
        self.ask_value_for_axis(x, y)

    def delete_axis(self, event):
        if self.value_entered:
            messagebox.showinfo("Info", "Please, Enter the value for the previous axis.")
            return

        x, y = event.x, event.y
        for index, axis in enumerate(self.axis_list):
            if axis[0] - 10 <= x <= axis[0] + 10 and axis[1] - 10 <= y <= axis[1] + 10:
                self.axis_list.pop(index)
                self.value_list.pop(index)
                self.axis_counter -= 1
                self.save_state()  # Save state after deleting an axis
                self.canvas.delete("all")
                self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, anchor=tk.CENTER, image=self.image_tk)
                for i, _axis in enumerate(self.axis_list):
                    self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
                    self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
                    self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
                    self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")
                for i, _point in enumerate(self.points):
                    self.canvas.create_oval(_point[0] - 2, _point[1] - 2, _point[0] + 2, _point[1] + 2, fill="blue")
                    point_text = f"X: {_point[0]}, Y: {_point[1]}"
                    self.canvas.create_text(_point[0], _point[1] - 20, text=point_text, fill="purple")

    def select_axis(self, event):
        x, y = event.x, event.y
        for index, axis in enumerate(self.axis_list):
            if axis[0] - 10 <= x <= axis[0] + 10 and axis[1] - 10 <= y <= axis[1] + 10:
                self.selected_axis = axis
                break

    def delete_point(self, event):
        x, y = event.x, event.y
        for index, point in enumerate(self.points):
            if point[0] - 2 <= x <= point[0] + 2 and point[1] - 2 <= y <= point[1] + 2:
                self.points.pop(index)
                self.canvas.delete("all")
                self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, anchor=tk.CENTER, image=self.image_tk)
                for i, _point in enumerate(self.points):
                    self.canvas.create_oval(_point[0] - 2, _point[1] - 2, _point[0] + 2, _point[1] + 2, fill="blue")
                    point_text = f"X: {_point[0]}, Y: {_point[1]}"
                    self.canvas.create_text(_point[0], _point[1] - 20, text=point_text, fill="purple")
                for i, _axis in enumerate(self.axis_list):
                    self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
                    self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
                    self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
                    self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")
                self.save_state()  # Save state after deleting a point

    def calculate_values(self):
        self.reset_button_colors()
        self.calculate_button_state = not self.calculate_button_state
        toggle_button_color(self.calculate_button, self.calculate_button_state)

        axis1 = self.axis_list[0]
        axis2 = self.axis_list[1]
        axis3 = self.axis_list[2]

        value1 = self.value_list[0]
        value2 = self.value_list[1]
        value3 = self.value_list[2]

        points = self.points

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

        for point in points:
            x = point[0]
            y = point[1]

            x_value = (x - x_min) / x_ratio

            coeffs = np.polyfit(y_list, y_value_list, 1)
            y_value = coeffs[0] * y + coeffs[1]

            self.point_values.append((x_value, y_value))

        print(self.point_values)

    def save_state(self):
        state = (self.axis_list.copy(), self.value_list.copy())
        self.history.append(state)
        self.redo_stack.clear()  # Clear the redo stack after a new state is saved

    def restore_state(self, state):
        self.axis_list, self.value_list = state
        self.axis_counter = len(self.axis_list)
        self.redraw_canvas()

    def clear_canvas(self):
        self.canvas.delete("all")
        if self.image_tk:
            self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, anchor=tk.CENTER, image=self.image_tk)
        self.draw_grid()

    def redraw_canvas(self):
        self.clear_canvas()
        for i, _axis in enumerate(self.axis_list):
            self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
            self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
            self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
            self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")
        for i, _point in enumerate(self.points):
            self.canvas.create_oval(_point[0] - 2, _point[1] - 2, _point[0] + 2, _point[1] + 2, fill="blue")
            point_text = f"X: {_point[0]}, Y: {_point[1]}"
            self.canvas.create_text(_point[0], _point[1] - 20, text=point_text, fill="purple")

    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.restore_state(self.history[-1])
        elif self.history:
            self.redo_stack.append(self.history.pop())
            self.clear_canvas()

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.history.append(state)
            self.restore_state(state)

    def toggle_geometry_window(self):
        if self.geometry_window:
            self.widgets.paned_window.forget(self.geometry_window.frame)
            self.geometry_window = None
        else:
            self.geometry_window = GeometryWindow(self.widgets.paned_window)
            self.widgets.paned_window.add(self.geometry_window.frame)

    def toggle_curve_fitting_window(self):
        if self.curve_fitting_window:
            self.widgets.paned_window.forget(self.curve_fitting_window.frame)
            self.curve_fitting_window = None
        else:
            self.curve_fitting_window = CurveFittingWindow(self.widgets.paned_window)
            self.widgets.paned_window.add(self.curve_fitting_window.frame)

    def show_original_image(self):
        self.show_image("original")

    def show_filtered_image(self):
        self.show_image("filtered")

    def hide_image(self):
        self.canvas.delete("all")

    def draw_grid(self):
        self.canvas.delete('grid_line')
        if not self.image_tk:
            return
        image_width = self.image_tk.width()
        image_height = self.image_tk.height()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x_offset = (canvas_width - image_width) // 2
        y_offset = (canvas_height - image_height) // 2
        for i in range(0, image_width, image_width // 5):
            self.canvas.create_line([(i + x_offset, y_offset), (i + x_offset, y_offset + image_height)], tag='grid_line', fill='gray')
        for i in range(0, image_height, image_height // 5):
            self.canvas.create_line([(x_offset, i + y_offset), (x_offset + image_width, i + y_offset)], tag='grid_line', fill='gray')

    def on_resize(self, event):
        self.canvas.config(width=event.width, height=event.height)
        self.redraw_canvas()

if __name__ == "__main__":
    root = tk.Tk()
    ImageViewer = ImageViewer(root)
    root.mainloop()
