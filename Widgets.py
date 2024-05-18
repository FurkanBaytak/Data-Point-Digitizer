import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from GeometryWindow import GeometryWindow
from CurveFittingWindow import CurveFittingWindow
from CurveListWindow import CurveListWindow

class Widgets:
    def __init__(self, viewer):
        self.viewer = viewer
        self.clipboard = ""
        self.history = []
        self.redo_stack = []
        self.geometry_window = None
        self.curve_fitting_window = None

    def create_widgets(self):
        menubar = tk.Menu(self.viewer.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Image", command=self.viewer.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.viewer.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_separator()
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Digitize menu
        digitize_menu = tk.Menu(menubar, tearoff=0)
        digitize_menu.add_command(label="Place Axis", accelerator="Shift+F3", command=self.viewer.show_axis)
        digitize_menu.add_command(label="Set Axis", accelerator="Shift+F4", command=self.viewer.set_axis)
        digitize_menu.add_command(label="Add Points", accelerator="Shift+F5", command=self.viewer.show_points)
        digitize_menu.add_command(label="Calculate", accelerator="Shift+F6", command=self.viewer.calculate_values)
        digitize_menu.add_command(label="Delete Curve", accelerator="Shift+F7", command=self.viewer.delete_curve)
        digitize_menu.add_command(label="Add Curve", accelerator="Shift+F8", command=self.viewer.add_curve)
        digitize_menu.add_command(label="Switch Curve", accelerator="Shift+F9", command=self.viewer.switch_curve)
        menubar.add_cascade(label="Digitize", menu=digitize_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(label="Curve Fitting Window", command=self.viewer.toggle_curve_fitting_window)
        view_menu.add_checkbutton(label="Geometry Window", command=self.viewer.toggle_geometry_window)
        view_menu.add_checkbutton(label="Grid Lines", command=self.toggle_grid_lines)
        view_menu.add_separator()

        # Background submenu
        self.background_var = tk.IntVar()
        background_menu = tk.Menu(view_menu, tearoff=0)
        background_menu.add_radiobutton(label="No Background", variable=self.background_var, value=0, command=self.viewer.hide_image)
        background_menu.add_radiobutton(label="Show Original Image", variable=self.background_var, value=1, command=self.viewer.show_original_image)
        background_menu.add_radiobutton(label="Show Filtered Image", variable=self.background_var, value=2, command=self.viewer.show_filtered_image)
        view_menu.add_cascade(label="Background", menu=background_menu)

        # Curves submenu
        self.curves_var = tk.IntVar()
        curves_menu = tk.Menu(view_menu, tearoff=0)
        curves_menu.add_radiobutton(label="Show Curves", variable=self.curves_var, value=0)
        curves_menu.add_radiobutton(label="Hide Curves", variable=self.curves_var, value=1)
        view_menu.add_cascade(label="Curves", menu=curves_menu)

        menubar.add_cascade(label="View", menu=view_menu)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Curve List", command=self.show_curve_list)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        self.viewer.root.config(menu=menubar)

        # Create and place the buttons in a frame
        button_frame = tk.Frame(self.viewer.root)
        button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.viewer.axis_button = tk.Button(button_frame, text="Place Axis", command=lambda: self.viewer.show_axis())
        self.viewer.axis_button.pack(pady=5)

        self.viewer.set_axis_button = tk.Button(button_frame, text="Set Axis", command=lambda: self.viewer.set_axis())
        self.viewer.set_axis_button.pack(pady=5)

        self.viewer.add_points_button = tk.Button(button_frame, text="Add Points", command=lambda: self.viewer.show_points())
        self.viewer.add_points_button.pack(pady=5)

        self.viewer.calculate_button = tk.Button(button_frame, text="Calculate", command=lambda: self.viewer.calculate_values())
        self.viewer.calculate_button.pack(pady=5)

        self.viewer.switch_curve_button = tk.Button(button_frame, text="Switch Curve", command=lambda: self.viewer.switch_curve())
        self.viewer.switch_curve_button.pack(pady=5, side=tk.BOTTOM)

        self.viewer.add_curve_button = tk.Button(button_frame, text="Add Curve", command=lambda: self.viewer.add_curve())
        self.viewer.add_curve_button.pack(pady=5, side=tk.BOTTOM)

        self.viewer.delete_curve_button = tk.Button(button_frame, text="Delete Curve", command=lambda: self.viewer.delete_curve())
        self.viewer.delete_curve_button.pack(pady=5, side=tk.BOTTOM)

        self.viewer.current_curve_label = tk.Label(button_frame, text=f"Current Curve: {self.viewer.current_curve} ")
        self.viewer.current_curve_label.pack(pady=5, side=tk.BOTTOM)

        # Create a PanedWindow to split the main area and the Geometry Window
        self.paned_window = tk.PanedWindow(self.viewer.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        # Create a frame for the main content and add it to the PanedWindow
        self.main_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.main_frame)

        # Create a canvas to display the image in the main frame
        self.viewer.canvas = tk.Canvas(self.main_frame, bg="white", width=800, height=600)
        self.viewer.canvas.pack(expand=True, fill=tk.BOTH)
        self.viewer.canvas.bind("<Button-1>", self.viewer.mouse_click)
        self.viewer.canvas.bind("<Button-3>", self.viewer.select_axis)

    def toggle_geometry_window(self):
        if self.geometry_window:
            self.paned_window.forget(self.geometry_window.frame)
            self.geometry_window = None
        else:
            self.geometry_window = GeometryWindow(self.paned_window)
            self.paned_window.add(self.geometry_window.frame)

    def toggle_grid_lines(self):
        self.viewer.grid_lines_visible = not self.viewer.grid_lines_visible
        if self.viewer.grid_lines_visible:
            self.viewer.draw_grid()
        else:
            self.viewer.canvas.delete('grid_line')

    def show_curve_list(self):
        CurveListWindow(self.viewer.root)

    def zoom_in(self):
        self.viewer.zoom_factor *= 1.2
        self.update_image_zoom()

    def zoom_out(self):
        self.viewer.zoom_factor /= 1.2
        self.update_image_zoom()

    def set_zoom_factor(self, ratio):
        if ratio == "Fill":
            self.zoom_fill()
        else:
            parts = ratio.split(":")
            if len(parts) == 2:
                width_ratio, height_ratio = map(int, parts)
                self.viewer.zoom_factor = width_ratio / height_ratio
                self.update_image_zoom()

    def zoom_fill(self):
        if self.viewer.image_original is not None:
            width = self.viewer.canvas.winfo_width()
            height = self.viewer.canvas.winfo_height()
            resized_image = self.viewer.image_original.resize((width, height), resample=Image.LANCZOS)
            self.viewer.image_tk = ImageTk.PhotoImage(resized_image)
            self.viewer.canvas.delete("all")
            self.viewer.canvas.create_image(0, 0, anchor=tk.CENTER, image=self.viewer.image_tk)

    def update_image_zoom(self):
        if self.viewer.image_original is not None:
            width = int(self.viewer.image_original.width * self.viewer.zoom_factor)
            height = int(self.viewer.image_original.height * self.viewer.zoom_factor)
            resized_image = self.viewer.image_original.resize((width, height), resample=Image.LANCZOS)
            self.viewer.image_tk = ImageTk.PhotoImage(resized_image)
            self.viewer.canvas.delete("all")
            self.viewer.canvas.create_image(0, 0, anchor=tk.CENTER, image=self.viewer.image_tk)

    def update_checkboxes(self, selected_var):
        if selected_var == self.viewer.hide_all_curves_var:
            self.viewer.show_selected_curve_var.set(False)
            self.viewer.show_all_curves_var.set(False)
        elif selected_var == self.viewer.show_selected_curve_var:
            self.viewer.hide_all_curves_var.set(False)
            self.viewer.show_all_curves_var.set(False)
        elif selected_var == self.viewer.show_all_curves_var:
            self.viewer.hide_all_curves_var.set(False)
            self.viewer.show_selected_curve_var.set(False)

    def set_current_curve(self, curve):
        self.viewer.current_curve_label.config(text=f"Current Curve: {curve}")
