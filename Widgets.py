import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class Widgets:
    def __init__(self, viewer):
        self.viewer = viewer
        self.clipboard = ""
        self.history = []
        self.redo_stack = []

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
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=self.cut)
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=self.copy)
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=self.paste)
        edit_menu.add_command(label="Delete", accelerator="Del", command=self.delete)
        edit_menu.add_separator()
        edit_menu.add_command(label="Paste As New", command=self.paste_as_new)
        edit_menu.add_command(label="Paste As New (Advanced)", command=self.paste_as_new_advanced)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Digitize menu
        digitize_menu = tk.Menu(menubar, tearoff=0)
        digitize_menu.add_command(label="Select Tool", accelerator="Shift+F2")
        digitize_menu.add_command(label="Axis Point Tool", accelerator="Shift+F3")
        digitize_menu.add_command(label="Scale Bar Tool", accelerator="Shift+F8")
        digitize_menu.add_command(label="Curve Point Tool", accelerator="Shift+F4")
        digitize_menu.add_command(label="Point Match Tool", accelerator="Shift+F5")
        digitize_menu.add_command(label="Color Picker Tool", accelerator="Shift+F6")
        digitize_menu.add_command(label="Segment Fill Tool", accelerator="Shift+F7")
        menubar.add_cascade(label="Digitize", menu=digitize_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)

        # Background Toolbar
        view_menu.add_checkbutton(label="Background Toolbar")
        view_menu.add_checkbutton(label="Digitizing Tools Toolbar")
        view_menu.add_checkbutton(label="Checklist Guide Toolbar")
        view_menu.add_checkbutton(label="Curve Fitting Window")
        view_menu.add_checkbutton(label="Geometry Window")
        view_menu.add_checkbutton(label="Settings Views Toolbar")
        view_menu.add_checkbutton(label="Coordinate System Toolbar")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Tool Tips")
        view_menu.add_checkbutton(label="Grid Lines")
        view_menu.add_separator()

        # Background submenu
        background_menu = tk.Menu(view_menu, tearoff=0)
        background_menu.add_command(label="Show Background")
        background_menu.add_command(label="Hide Background")
        view_menu.add_cascade(label="Background", menu=background_menu)

        # Curves submenu
        curves_menu = tk.Menu(view_menu, tearoff=0)
        curves_menu.add_command(label="Show Curves")
        curves_menu.add_command(label="Hide Curves")
        view_menu.add_cascade(label="Curves", menu=curves_menu)

        # Status Bar submenu
        status_bar_menu = tk.Menu(view_menu, tearoff=0)
        status_bar_menu.add_command(label="Show Status Bar")
        status_bar_menu.add_command(label="Hide Status Bar")
        view_menu.add_cascade(label="Status Bar", menu=status_bar_menu)

        # Zoom submenu
        zoom_menu = tk.Menu(view_menu, tearoff=0)
        zoom_menu.add_command(label="Zoom In", command=self.zoom_in)
        zoom_menu.add_command(label="Zoom Out", command=self.zoom_out)
        zoom_menu.add_separator()
        zoom_ratios = ["16:1", "8:1", "4:1", "2:1", "1:1", "1:2", "1:4", "1:8", "1:16", "Fill"]
        for _ratio in zoom_ratios:
            zoom_menu.add_command(label=_ratio, command=lambda ratio=_ratio: self.set_zoom_factor(ratio))
        view_menu.add_cascade(label="Zoom", menu=zoom_menu)

        menubar.add_cascade(label="View", menu=view_menu)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Coordinates")
        settings_menu.add_command(label="Curve List")
        settings_menu.add_command(label="Curve Properties")
        settings_menu.add_command(label="Digitize Curve")
        settings_menu.add_command(label="Export Format")
        settings_menu.add_command(label="Color Filter")
        settings_menu.add_command(label="Axes Checker")
        settings_menu.add_command(label="Grid Line Display")
        settings_menu.add_command(label="Grid Line Removal")
        settings_menu.add_command(label="Point Match")
        settings_menu.add_command(label="Segment Fill")
        settings_menu.add_separator()
        settings_menu.add_command(label="General")
        settings_menu.add_command(label="Main Window")
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

        self.viewer.current_curve_label = tk.Label(button_frame, text=f"Current Curve:{self.viewer.current_curve} ")
        self.viewer.current_curve_label.pack(pady=5, side=tk.BOTTOM)

        # Create a canvas to display the image
        self.viewer.canvas = tk.Canvas(self.viewer.root, bg="white", width=800, height=600)
        self.viewer.canvas.pack(expand=True, fill=tk.BOTH)
        self.viewer.canvas.bind("<Button-1>", self.viewer.mouse_click)
        self.viewer.canvas.bind("<Button-3>", self.viewer.select_axis)

        self.viewer.checklist = tk.Listbox(self.viewer.root, selectmode=tk.MULTIPLE)
        self.viewer.checklist.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

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
            self.viewer.canvas.create_image(0, 0, anchor=tk.NW, image=self.viewer.image_tk)

    def update_image_zoom(self):
        if self.viewer.image_original is not None:
            width = int(self.viewer.image_original.width * self.viewer.zoom_factor)
            height = int(self.viewer.image_original.height * self.viewer.zoom_factor)
            resized_image = self.viewer.image_original.resize((width, height), resample=Image.LANCZOS)
            self.viewer.image_tk = ImageTk.PhotoImage(resized_image)
            self.viewer.canvas.delete("all")
            self.viewer.canvas.create_image(0, 0, anchor=tk.NW, image=self.viewer.image_tk)

    def hide_all_curves(self):
        self.update_checkboxes(self.viewer.hide_all_curves_var)
        # tbc

    def show_selected_curve(self):
        self.update_checkboxes(self.viewer.show_selected_curve_var)
        # tbc

    def show_all_curves(self):
        self.update_checkboxes(self.viewer.show_all_curves_var)
        # tbc

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

    def undo(self):
        if self.history:
            state = self.history.pop()
            self.redo_stack.append(state)
            # Restore the previous state
            if self.history:
                self.restore_state(self.history[-1])
            else:
                self.clear_canvas()

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.history.append(state)
            self.restore_state(state)

    def cut(self):
        self.copy()
        self.delete()

    def copy(self):
        selected = self.viewer.canvas.find_withtag("current")
        if selected:
            self.clipboard = self.viewer.canvas.itemcget(selected, "text")

    def paste(self):
        if self.clipboard:
            x, y = self.viewer.canvas.winfo_pointerxy()
            self.viewer.canvas.create_text(x, y, text=self.clipboard)
            self.save_state()

    def delete(self):
        selected = self.viewer.canvas.find_withtag("current")
        if selected:
            self.viewer.canvas.delete(selected)
            self.save_state()

    def paste_as_new(self):
        if self.clipboard:
            self.viewer.canvas.create_text(400, 300, text=self.clipboard)  # Paste in the center
            self.save_state()

    def paste_as_new_advanced(self):
        if self.clipboard:
            self.viewer.canvas.create_text(400, 300, text=self.clipboard, font=("Helvetica", 12, "bold"), fill="blue")
            self.save_state()

    def save_state(self):
        # Save the current state of the canvas
        items = self.viewer.canvas.find_all()
        state = [(self.viewer.canvas.coords(item), self.viewer.canvas.itemcget(item, "text")) for item in items]
        self.history.append(state)

    def restore_state(self, state):
        self.clear_canvas()
        for coords, text in state:
            self.viewer.canvas.create_text(coords, text=text)

    def clear_canvas(self):
        self.viewer.canvas.delete("all")


    def set_current_curve(self, curve):
        self.viewer.current_curve_label.config(text=f"Current Curve: {curve}")