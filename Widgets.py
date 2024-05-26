import tkinter as tk
from PIL import Image, ImageTk
from GeometryWindow import GeometryWindow
from CurveSettingsWindow import CurveSettingsWindow
from GridSettings import GridSettings
from EditCurveList import EditCurveList


class Widgets:
    def __init__(self, viewer):
        """
        Initialize the Widgets class.

        Parameters:
        viewer (Viewer): An instance of a viewer class that provides data.
        """
        self.edit_curve_list = None
        self.main_frame = None
        self.background_var = None
        self.paned_window = None
        self.viewer = viewer
        self.clipboard = ""
        self.history = []
        self.redo_stack = []
        self.geometry_window = None

    def create_widgets(self):
        """
        Create and place all the widgets in the main application window.
        """
        menubar = tk.Menu(self.viewer.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Image", command=self.viewer.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.viewer.root.quit)
        file_menu.add_separator()
        file_menu.add_command(label="Export", command=self.viewer.export_data)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_separator()
        edit_menu.add_command(label="Curve List", command=self.open_list_window)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Digitize menu
        digitize_menu = tk.Menu(menubar, tearoff=0)
        digitize_menu.add_command(label="Place Axis", command=self.viewer.show_axis)
        digitize_menu.add_command(label="Set Axis", command=self.viewer.set_axis)
        digitize_menu.add_command(label="Add Points", command=self.viewer.show_points)
        digitize_menu.add_command(label="Calculate", command=self.viewer.calculate_values)
        digitize_menu.add_command(label="Delete Curve", command=self.viewer.delete_curve)
        digitize_menu.add_command(label="Add Curve", command=self.viewer.add_curve)
        digitize_menu.add_command(label="Switch Curve", command=self.viewer.switch_curve)
        menubar.add_cascade(label="Digitize", menu=digitize_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(label="Geometry Window", command=self.toggle_geometry_window)
        view_menu.add_checkbutton(label="Grid Lines", command=self.toggle_grid_lines)
        view_menu.add_separator()

        # Background submenu
        self.background_var = tk.IntVar()
        background_menu = tk.Menu(view_menu, tearoff=0)
        background_menu.add_radiobutton(label="No Background", variable=self.background_var, value=0,
                                        command=self.viewer.hide_image)
        background_menu.add_radiobutton(label="Show Original Image", variable=self.background_var, value=1,
                                        command=self.viewer.show_original_image)
        background_menu.add_radiobutton(label="Show Filtered Image", variable=self.background_var, value=2,
                                        command=self.viewer.show_filtered_image)
        view_menu.add_cascade(label="Background", menu=background_menu)
        menubar.add_cascade(label="View", menu=view_menu)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Curve Settings",
                                  command=lambda: CurveSettingsWindow(self.viewer).open_settings_window())
        settings_menu.add_command(label="Grid Settings",
                                  command=lambda: GridSettings(self.viewer).open_settings_window())
        menubar.add_cascade(label="Settings", menu=settings_menu)

        self.viewer.root.config(menu=menubar)

        # Create and place the buttons in a frame
        button_frame = tk.Frame(self.viewer.root)
        button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.viewer.axis_button = tk.Button(button_frame, text="Place Axis", command=self.viewer.show_axis)
        self.viewer.axis_button.pack(pady=5)

        self.viewer.set_axis_button = tk.Button(button_frame, text="Set Axis", command=self.viewer.set_axis)
        self.viewer.set_axis_button.pack(pady=5)

        self.viewer.add_points_button = tk.Button(button_frame, text="Add Points", command=self.viewer.show_points)
        self.viewer.add_points_button.pack(pady=5)

        self.viewer.calculate_button = tk.Button(button_frame, text="Calculate", command=self.viewer.calculate_values)
        self.viewer.calculate_button.pack(pady=5)

        self.viewer.switch_curve_button = tk.Button(button_frame, text="Switch Curve", command=self.viewer.switch_curve)
        self.viewer.switch_curve_button.pack(pady=5, side=tk.BOTTOM)

        self.viewer.add_curve_button = tk.Button(button_frame, text="Add Curve", command=self.viewer.add_curve)
        self.viewer.add_curve_button.pack(pady=5, side=tk.BOTTOM)

        self.viewer.delete_curve_button = tk.Button(button_frame, text="Delete Curve", command=self.viewer.delete_curve)
        self.viewer.delete_curve_button.pack(pady=5, side=tk.BOTTOM)

        self.viewer.current_curve_label = tk.Label(button_frame,
                                                   text=f"{self.viewer.curve_names[self.viewer.current_curve - 1]}")
        self.viewer.current_curve_label.pack(pady=5, side=tk.BOTTOM)

        self.viewer.current_curve_text = tk.Label(button_frame, text="Current Curve:")
        self.viewer.current_curve_text.pack(pady=5, side=tk.BOTTOM)

        self.viewer.selected_axis_text = tk.Label(button_frame, text="Selected axis:")
        self.viewer.selected_axis_text.pack(pady=10)

        self.viewer.selected_axis_label = tk.Label(button_frame, text=f"{self.viewer.selected_axis}")
        self.viewer.selected_axis_label.pack()

        self.paned_window = tk.PanedWindow(self.viewer.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        self.main_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.main_frame)

        # Create a canvas to display the image in the main frame
        self.viewer.canvas = tk.Canvas(self.main_frame, bg="white", width=800, height=600)
        self.viewer.canvas.pack(expand=True, fill=tk.BOTH)
        self.viewer.canvas.bind("<Button-1>", self.viewer.mouse_click)
        self.viewer.canvas.bind("<Button-3>", self.viewer.select_axis)

    def toggle_geometry_window(self):
        """
        Toggle the visibility of the Geometry Window.
        """
        if self.geometry_window:
            self.paned_window.forget(self.geometry_window.frame)
            self.geometry_window = None
        else:
            self.geometry_window = GeometryWindow(self.paned_window, self.viewer)
            self.paned_window.add(self.geometry_window.frame)

    def toggle_grid_lines(self):
        """
        Toggle the visibility of grid lines.
        """
        self.viewer.grid_lines_visible = not self.viewer.grid_lines_visible
        if self.viewer.grid_lines_visible:
            self.viewer.draw_grid()
        else:
            self.viewer.canvas.delete('grid_line')

    def zoom_in(self):
        """
        Zoom in the image by increasing the zoom factor.
        """
        self.viewer.zoom_factor *= 1.2
        self.update_image_zoom()

    def zoom_out(self):
        """
        Zoom out the image by decreasing the zoom factor.
        """
        self.viewer.zoom_factor /= 1.2
        self.update_image_zoom()

    def set_zoom_factor(self, ratio):
        """
        Set the zoom factor based on the given ratio.

        Parameters:
        ratio (str): The zoom ratio in the format "width:height".
        """
        if ratio == "Fill":
            self.zoom_fill()
        else:
            parts = ratio.split(":")
            if len(parts) == 2:
                width_ratio, height_ratio = map(int, parts)
                self.viewer.zoom_factor = width_ratio / height_ratio
                self.update_image_zoom()

    def zoom_fill(self):
        """
        Zoom the image to fill the entire canvas.
        """
        if self.viewer.image_original is not None:
            width = self.viewer.canvas.winfo_width()
            height = self.viewer.canvas.winfo_height()
            resized_image = self.viewer.image_original.resize((width, height), resample=Image.LANCZOS)
            self.viewer.image_tk = ImageTk.PhotoImage(resized_image)
            self.viewer.canvas.delete("all")
            self.viewer.canvas.create_image(0, 0, anchor=tk.CENTER, image=self.viewer.image_tk)

    def update_image_zoom(self):
        """
        Update the zoom level of the image based on the current zoom factor.
        """
        if self.viewer.image_original is not None:
            width = int(self.viewer.image_original.width * self.viewer.zoom_factor)
            height = int(self.viewer.image_original.height * self.viewer.zoom_factor)
            resized_image = self.viewer.image_original.resize((width, height), resample=Image.LANCZOS)
            self.viewer.image_tk = ImageTk.PhotoImage(resized_image)
            self.viewer.canvas.delete("all")
            self.viewer.canvas.create_image(0, 0, anchor=tk.CENTER, image=self.viewer.image_tk)

    def set_current_curve(self, curve):
        """
        Set the label for the current curve.

        Parameters:
        curve (str): The name of the current curve.
        """
        self.viewer.current_curve_label.config(text=curve)

    def set_selected_axis(self, axis):
        """
        Set the label for the selected axis.

        Parameters:
        axis (str): The name of the selected axis.
        """
        self.viewer.selected_axis_label.config(text=axis)

    def open_list_window(self):
        """
        Open the window to edit the curve list.
        """
        if self.edit_curve_list is None:
            self.edit_curve_list = EditCurveList(self.viewer)
        self.edit_curve_list.open_list_window()
