import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
from PIL import Image, ImageTk

# a
class ImageViewer:

    def __init__(self, _root):
        self.calculate_button = None
        self.add_points_button = None
        self.set_axis_button = None
        self.canvas = None
        self.root = _root
        self.root.title("Show Image")
        self.zoom_factor = 1.2

        self.create_widgets()

        self.open_image_button = None
        self.image_original = None
        self.image_tk = None

        self.axis_button = None
        self.axis_state = True
        self.axis_list = []
        self.value_list = []
        self.value_entered = False
        self.axis_counter = 0
        self.selected_axis = None

        self.points = []
        self.point_values = []

        self.checklist = None

    def create_widgets(self):
        self.open_image_button = tk.Button(self.root, text="Open Image", command=self.open_image)
        self.open_image_button.pack(pady=10)

        self.axis_button = tk.Button(self.root, text="place axis", command=lambda: self.show_axis())
        self.axis_button.pack(pady=10, side=tk.LEFT)

        self.set_axis_button = tk.Button(self.root, text="set axis", command=lambda: self.set_axis())
        self.set_axis_button.pack(pady=10, side=tk.LEFT, padx=10)

        self.add_points_button = tk.Button(self.root, text="Add Points", command=lambda: self.show_points())
        self.add_points_button.pack(pady=10, side=tk.LEFT, padx=10)

        self.calculate_button = tk.Button(self.root, text="Calculate", command=lambda: self.calculate_values())
        self.calculate_button.pack(pady=10, side=tk.LEFT, padx=10)

        # Create a canvas to display the image
        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=600)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.mouse_click)
        self.canvas.bind("<Button-3>", self.select_axis)

        self.checklist = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.checklist.pack(pady=10)


    @staticmethod
    def format_control(file_path):
        # File format control
        if file_path.endswith(".jpg") or file_path.endswith(".jpeg") or file_path.endswith(".png"):
            return True
        return False

    def open_image(self):
        # Select an image file
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                # Resmi aç
                self.image_original = Image.open(file_path)
                if not self.format_control(file_path):
                    raise messagebox.showerror("Error", "Image format is not supported!"
                                                        " Please select a valid image file.")
                self.image_original = self.image_original.resize((800, 600), Image.Resampling.LANCZOS)
                self.image_tk = ImageTk.PhotoImage(self.image_original)

                # Delete all items on the canvas
                self.canvas.delete("all")

                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

            except (IOError, SyntaxError):
                # Raise an error if the file is not a valid image file
                raise messagebox.showerror("Hata", "Image file is not valid! Please select a valid image file.")

    def mouse_click(self, event):
        if hasattr(self.root, "label"):
            self.root.label.destroy()  # İf the label exists, destroy it
        self.root.label = tk.Label(self.root, text=f"X: {event.x}, Y: {event.y}")
        self.root.label.place(x=event.x, y=event.y)
        self.root.label.pack()

    def show_axis(self):
        if self.axis_state:
            self.canvas.bind("<Button-1>", self.place_axis)
            self.canvas.bind("<Button-3>", self.delete_axis)

            self.axis_state = False
        else:
            self.canvas.bind("<Button-1>", self.mouse_click)
            self.canvas.bind("<Button-3>", self.select_axis)
            self.axis_state = True

    def show_points(self):
        if self.axis_state:
            self.canvas.bind("<Button-1>", self.add_points)
            self.canvas.bind("<Button-3>", self.delete_point)
            self.axis_state = False
        else:
            self.canvas.bind("<Button-1>", self.mouse_click)
            self.canvas.bind("<Button-3>", self.select_axis)
            self.axis_state = True

    def place_axis(self, event):
        if self.value_entered:
            messagebox.showinfo("Info", "Please, Enter the value for the previous axis.")
            return
        if self.axis_counter == 3:
            messagebox.showinfo("Info", "You can only add 4 axes.")
            return

        x, y = event.x, event.y
        self.canvas.create_line(x - 10, y, x + 10, y, fill="red", width=1)
        self.canvas.create_line(x, y - 10, x, y + 10, fill="red", width=1)

        value_text = f"X: {x}, Y: {y}"
        self.canvas.create_text(x, y - 20, text=value_text, fill="blue")
        self.axis_list.append((x, y))
        self.axis_counter += 1
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
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
                for i, _axis in enumerate(self.axis_list):
                    self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
                    self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
                    self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
                    self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")
                for i, ponint in enumerate(self.points):
                    self.canvas.create_oval(ponint[0] - 2, ponint[1] - 2, ponint[0] + 2, ponint[1] + 2, fill="blue")
                    point_text = f"X: {ponint[0]}, Y: {ponint[1]}"
                    self.canvas.create_text(ponint[0], ponint[1] - 20, text=point_text, fill="purple")

    def select_axis(self, event):
        x, y = event.x, event.y
        for index, axis in enumerate(self.axis_list):
            if axis[0] - 10 <= x <= axis[0] + 10 and axis[1] - 10 <= y <= axis[1] + 10:
                self.selected_axis = axis
                break

    def set_axis(self):
        if not self.selected_axis:
            messagebox.showinfo("Error", "Please, Select a axis.")
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

        confirm_button = tk.Button(set_axis_window, text="Confirm", command=lambda: self.confirm_axis(set_axis_window,
                                                                                                      x_entry, y_entry))
        confirm_button.grid(row=2, column=0, columnspan=2, pady=10)

    def confirm_axis(self, window, x_entry, y_entry):
        print(self.selected_axis)
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
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
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
        window.destroy()  # Close the window

    def ask_value_for_axis(self, x, y):
        self.value_entered = True

        value_window = tk.Toplevel(self.root)
        value_window.title("Add Value")

        value_x_label = tk.Label(value_window, text="Value for X:")
        value_x_label.grid(row=0, column=0, padx=5, pady=5)
        value_x_entry = tk.Entry(value_window)
        value_x_entry.grid(row=0, column=1, padx=5, pady=5)

        value_y_label = tk.Label(value_window, text="Value for Y:")
        value_y_label.grid(row=1, column=0, padx=5, pady=5)
        value_y_entry = tk.Entry(value_window)
        value_y_entry.grid(row=1, column=1, padx=5, pady=5)

        value_button = tk.Button(value_window, text="Add Value",
                                 command=lambda: self.add_value_to_axis(value_x_entry.get(), value_y_entry.get(), x, y,
                                                                        value_window))
        value_button.grid(row=2, column=0, columnspan=2, pady=10)

    def add_value_to_axis(self, value_x, value_y, x, y, value_window):
        # İf the value is not a digit, show an error message
        if value_x.isdigit() and value_y.isdigit():
            value_x = int(value_x)
            value_y = int(value_y)
            self.canvas.create_text(x, y + 10, text=f"value X: {value_x}, Y: {value_y}", fill="green")
            self.value_list.append((value_x, value_y))
            print(self.value_list)
            value_window.destroy()  # Close the window
        else:
            messagebox.showerror("Error", "Please, Enter valid values for X and Y.")
        self.value_entered = False

    def add_points(self, event):
        if self.axis_counter < 3:
            messagebox.showinfo("Info", "Please, Add at least 3 axis to add points.")
            return
        x, y = event.x, event.y
        self.points.append((x, y))
        self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="blue")
        point_text = f"X: {x}, Y: {y}"
        self.canvas.create_text(x, y - 20, text=point_text, fill="purple")

    def delete_point(self, event):
        x, y = event.x, event.y
        for index, point in enumerate(self.points):
            if point[0] - 2 <= x <= point[0] + 2 and point[1] - 2 <= y <= point[1] + 2:
                self.points.pop(index)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
                for i,ponint in enumerate(self.points):
                    self.canvas.create_oval(ponint[0] - 2, ponint[1] - 2, ponint[0] + 2, ponint[1] + 2, fill="blue")
                    point_text = f"X: {ponint[0]}, Y: {ponint[1]}"
                    self.canvas.create_text(ponint[0], ponint[1] - 20, text=point_text, fill="purple")
                for i, _axis in enumerate(self.axis_list):
                    self.canvas.create_line(_axis[0] - 10, _axis[1], _axis[0] + 10, _axis[1], fill="red", width=1)
                    self.canvas.create_line(_axis[0], _axis[1] - 10, _axis[0], _axis[1] + 10, fill="red", width=1)
                    self.canvas.create_text(_axis[0], _axis[1] - 20, text=f"X: {_axis[0]}, Y: {_axis[1]}", fill="blue")
                    self.canvas.create_text(_axis[0], _axis[1] + 10, text=f"value: {self.value_list[i]}", fill="green")

    def calculate_values(self):
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
        y_min = min(y_list)
        y_max = max(y_list)

        x_value_min = min(x_value_list)
        x_value_max = max(x_value_list)
        y_value_min = min(y_value_list)
        y_value_max = max(y_value_list)

        x_diff = abs(x_max) - abs(x_min)
        y_diff = abs(y_max) - abs(y_min)

        x_value_diff = x_value_max - x_value_min
        y_value_diff = y_value_min - y_value_max

        x_ratio = x_diff / x_value_diff
        y_ratio = y_diff / y_value_diff



        for point in points:
            x = point[0]
            y = point[1]

            x_value = (x - x_min) / x_ratio

            coeffs = np.polyfit(y_list, y_value_list, 1)
            y_value = coeffs[0] * y + coeffs[1]


            self.point_values.append((x_value, y_value))

        print(self.point_values)











root = tk.Tk()

ImageViewer = ImageViewer(root)

root.mainloop()