import copy
import tkinter as tk
from tkinter import ttk


class GeometryWindow:
    def __init__(self, parent, viewer):
        """
        Initialize the GeometryWindow class.

        Parameters:
        parent (tk.Tk or tk.Widget): The parent widget.
        viewer (Viewer): An instance of a viewer class that provides data.
        """
        self.viewer = viewer
        self.frame = tk.Frame(parent, width=320, bg="grey")
        self.label = tk.Label(self.frame, text="Geometry Window", bg="grey")
        self.label.pack(side=tk.TOP, fill=tk.X)

        self.tree = ttk.Treeview(self.frame, columns=("Curves", "Points", "X", "Y"), show="headings")
        self._configure_tree()
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.populate_tree()

    def _configure_tree(self):
        """
        Configure the treeview widget's headings and columns.
        """
        headings = ["Curves", "Points", "X", "Y"]
        for heading in headings:
            self.tree.heading(heading, text=heading)
            self.tree.column(heading, anchor=tk.CENTER, stretch=tk.NO, width=80)

    def populate_tree(self):
        """
        Populate the treeview with data from the viewer.
        """
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Retrieve data
        data = self.viewer.data_values
        curves = self.viewer.curves

        curve_values = self._deep_copy_curves(curves, data)
        self._insert_data_into_tree(curve_values)

    @staticmethod
    def _deep_copy_curves(curves, data):
        """
        Deep copy curves and update with data values.

        Parameters:
        curves (list): List of curves.
        data (list): List of data values.

        Returns:
        list: Updated list of curve values.
        """
        curve_values = copy.deepcopy(curves)
        for i, curve in enumerate(curves):
            if curve:  # Check if the sublist is not empty
                for j in range(len(curve)):
                    if j < len(data[0]):  # Ensure index does not exceed the data list length
                        curve_values[i][j] = data[0][j]
        return curve_values

    def _insert_data_into_tree(self, curve_values):
        """
        Insert data into the treeview.

        Parameters:
        curve_values (list): List of updated curve values.
        """
        for i, curve in enumerate(curve_values):
            if curve:
                for j, value in enumerate(curve):
                    self.tree.insert("", tk.END, values=(
                        self.viewer.curve_names[i], j + 1, value[0], value[1]
                    ))
