import tkinter as tk
from tkinter import ttk

class GeometryWindow:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.label = tk.Label(self.frame, text="Geometry Window", bg="lightgrey")
        self.label.pack(side=tk.TOP, fill=tk.X)

        self.tree = ttk.Treeview(self.frame, columns=("X", "Y", "Index", "Distance"), show="headings")
        self.tree.heading("X", text="X")
        self.tree.heading("Y", text="Y")
        self.tree.heading("Index", text="Index")
        self.tree.heading("Distance", text="Distance")
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.populate_tree()

    def populate_tree(self):
        # Sample data
        sample_data = [
            (1, 2, 1, 3.5),
            (4, 5, 2, 7.1),
            (7, 8, 3, 1.2)
        ]
        for item in sample_data:
            self.tree.insert("", "end", values=item)
