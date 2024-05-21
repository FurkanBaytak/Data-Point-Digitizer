import tkinter as tk
from tkinter import ttk


class GeometryWindow:
    def __init__(self, parent, viewer):
        self.viewer = viewer
        self.frame = tk.Frame(parent, width=320, bg="grey")
        self.label = tk.Label(self.frame, text="Geometry Window", bg="grey")
        self.label.pack(side=tk.TOP, fill=tk.X)

        self.tree = ttk.Treeview(self.frame, columns=("Curve", "points", "X", "Y"), show="headings")
        self.tree.heading("Curve", text="Curve",)
        self.tree.heading("points", text="Points")
        self.tree.heading("X", text="X")
        self.tree.heading("Y", text="Y")
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.tree.column("Curve", anchor=tk.CENTER, stretch=tk.NO, width=80)
        self.tree.column("points", anchor=tk.CENTER, stretch=tk.NO, width=80)
        self.tree.column("X", anchor=tk.CENTER, stretch=tk.NO, width=80)
        self.tree.column("Y", anchor=tk.CENTER, stretch=tk.NO, width=80)

        self.populate_tree()

    def populate_tree(self):
        # Sample data
        data = self.viewer.data_values
        for i, curve in enumerate(data):
            for j, point in enumerate(curve):
                self.tree.insert("", tk.END, values=(f"Curve {i+1}", f"Point {j+1}", point[0], point[1]))
