import tkinter as tk

from GUI.RelativeMap import RelativeMap


class RelativeMapGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Relatvie Map GUI")
        self.constraints = []

        self.image_drawer = RelativeMap()
        self.image_drawer.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.room1 = tk.StringVar(self.root)
        self.room2 = tk.StringVar(self.root)
        self.direction = tk.StringVar(self.root)

        self.room1.set("Room 1")
        self.room2.set("Room 2")
        self.direction.set("Direction")

        self.room1_drop = tk.OptionMenu(self.root, self.room1, "A", "B", "C", "D")
        self.room2_drop = tk.OptionMenu(self.root, self.room2, "A", "B", "C", "D")
        self.direction_drop = tk.OptionMenu(self.root, self.direction, "left", "right", "top", "bottom")

        self.room1_drop.pack(side=tk.LEFT)
        self.room2_drop.pack(side=tk.LEFT)
        self.direction_drop.pack(side=tk.LEFT)

        # Create a button to add the constraint
        self.add_constraint_button = tk.Button(self.root, text="Add Constraint", command=self.add_constraint)
        self.add_constraint_button.pack(side=tk.LEFT)

        # Add a button to clear the constraints
        self.clear_button = tk.Button(self.root, text="Clear Constraints", command=self.clear_constraints)
        self.clear_button.pack(side=tk.LEFT)

        # Add a text display for the constraints
        self.constraint_display = tk.Text(self.root, height=10, width=50)
        self.constraint_display.pack(side=tk.LEFT)


    def add_constraint(self):
        # The constraint from the drop down menu will be add to the constraint display first
        room1 = self.room1.get()
        room2 = self.room2.get()
        direction = self.direction.get()
        self.constraint_display.insert(tk.END, f"{room1} {direction} {room2}\n")
        self.constraints.append((room1, room2, direction))

        # Add the constraint to the image drawer
        self.image_drawer.update_plot(self.constraints, new_sizes={"A": (2, 2), "B": (2, 1), "C": (1, 1), "D": (1, 1)})

    def clear_constraints(self):
        self.constraint_display.delete(1.0, tk.END)
        self.constraints = []
        self.image_drawer.update_plot(self.constraints)




if __name__ == "__main__":
    root = tk.Tk()
    app = RelativeMapGUI(root)
    root.mainloop()
