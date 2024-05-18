import tkinter as tk
from tkinter import ttk

class CurveFittingWindow:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.label = tk.Label(self.frame, text="Curve Fitting Window", bg="lightgrey")
        self.label.pack(side=tk.TOP, fill=tk.X)

        self.tree = ttk.Treeview(self.frame, columns=("Order", "Curve"), show="headings")
        self.tree.heading("Order", text="Order")
        self.tree.heading("Curve", text="Curve")
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.populate_tree()

    def populate_tree(self):
        # Sample data
        sample_data = [
            (2, "X^2 +"),
            (1, "X +"),
        ]
        for item in sample_data:
            self.tree.insert("", "end", values=item)
