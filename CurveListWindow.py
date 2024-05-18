import tkinter as tk


class CurveListWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Curve List")

        self.curve_names = ["Curve1"]

        self.listbox = tk.Listbox(self.window)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for curve in self.curve_names:
            self.listbox.insert(tk.END, curve)

        self.add_button = tk.Button(self.window, text="Add", command=self.add_curve)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.remove_button = tk.Button(self.window, text="Remove", command=self.remove_curve)
        self.remove_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(self.window, text="Save As Default", command=self.save_default)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_button = tk.Button(self.window, text="Reset Default", command=self.reset_default)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.ok_button = tk.Button(self.window, text="Ok", command=self.window.destroy)
        self.ok_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.cancel_button = tk.Button(self.window, text="Cancel", command=self.window.destroy)
        self.cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

    def add_curve(self):
        curve_name = f"Curve{len(self.curve_names) + 1}"
        self.curve_names.append(curve_name)
        self.listbox.insert(tk.END, curve_name)

    def remove_curve(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            self.curve_names.pop(selected_index[0])
            self.listbox.delete(selected_index)

    def save_default(self):
        # needs implementation or removal
        print("Saved as default:", self.curve_names)

    def reset_default(self):
        # needs implementation or removal
        print("Reset to default")
