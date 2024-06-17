import tkinter as tk
from tkinter import ttk

from src.frontend.components.RelativeMapMaxMin import RelativeMapMaxMin


class RelativeInputFrame(tk.Frame):
    def __init__(self, rooms, add_constraint, clear_constraints):
        super().__init__()
        self.rooms = list(rooms)
        self.add_constraint = add_constraint
        self.clear_constraints = clear_constraints

        self.room_1 = tk.StringVar()
        self.room_2 = tk.StringVar()
        self.direction = tk.StringVar()
        self.room_1.set("Room 1")
        self.room_2.set("Room 2")
        self.direction.set("Direction")

        self.room_drop_menu_1 = ttk.Combobox(self, textvariable=self.room_1, values=["None"] + self.rooms, state='readonly')
        self.room_drop_menu_2 = ttk.Combobox(self, textvariable=self.room_2, values=["None"] + self.rooms, state='readonly')
        self.direction_drop_menu = ttk.Combobox(self, textvariable=self.direction, values=["west", "east", "north", "south"], state='readonly')

        self.room_drop_menu_1.pack(side=tk.LEFT, padx=5)
        self.room_drop_menu_2.pack(side=tk.LEFT, padx=5)
        self.direction_drop_menu.pack(side=tk.LEFT, padx=5)

        self.add_constraint_button = ttk.Button(self, text="Add Constraint", command=self.add_constraint_button_helper)
        self.add_constraint_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(self, text="Clear Constraints", command=self.clear_constraint_button_helper)
        self.clear_button.pack(side=tk.LEFT, padx=5)

    def add_constraint_button_helper(self):
        room1 = self.room_1.get()
        room2 = self.room_2.get()
        direction = self.direction.get()

        if room1 != "Room 1" and room2 != "Room 2" and direction != "Direction" and room1 is not None and room2 is not None:
            self.add_constraint(room1, room2, direction)

    def clear_constraint_button_helper(self):
        self.clear_constraints()

    def update_room_list(self, rooms):
        self.rooms = rooms
        room_list = ["None"] + list(rooms)

        self.room_drop_menu_1['values'] = room_list
        self.room_drop_menu_2['values'] = room_list

        self.room_drop_menu_1.set("None")
        self.room_drop_menu_2.set("None")


class RoomInputFrame(tk.Frame):
    # The frame component containing the input for adding rooms
    def __init__(self, add_room, clear_rooms):
        super().__init__()
        self.add_room = add_room
        self.clear_rooms = clear_rooms

        self.room_name = tk.StringVar(self)
        self.height = tk.StringVar(self)
        self.width = tk.StringVar(self)

        ttk.Label(self, text="Room Name:").pack(side=tk.LEFT)
        self.room_name_input = ttk.Entry(self, textvariable=self.room_name, width=20)
        self.room_name_input.pack(side=tk.LEFT, padx=5)

        ttk.Label(self, text="Height:").pack(side=tk.LEFT)
        self.room_x_input = ttk.Entry(self, textvariable=self.height, width=7)
        self.room_x_input.pack(side=tk.LEFT, padx=5)

        ttk.Label(self, text="Width:").pack(side=tk.LEFT)
        self.room_y_input = ttk.Entry(self, textvariable=self.width, width=7)
        self.room_y_input.pack(side=tk.LEFT, padx=5)

        self.add_room_button = ttk.Button(self, text="Add Room", command=self.add_room_button_helper)
        self.add_room_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(self, text="Clear Rooms", command=self.clear_room_button_helper)
        self.clear_button.pack(side=tk.LEFT, padx=5)

    def add_room_button_helper(self):
        room_name = self.room_name.get()
        height = self.height.get()
        width = self.width.get()

        if room_name and height and width:
            self.add_room(room_name, height, width)

    def clear_room_button_helper(self):
        self.clear_rooms()


class RelativeMapGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Relatvie Map GUI")
        self.constraints = []
        self.sizes = {}

        self.image_drawer = RelativeMapMaxMin()
        self.image_drawer.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Create a frame for the input
        self.input_frame = RelativeInputFrame(rooms=self.sizes.keys(), add_constraint=self.add_constraint,
                                              clear_constraints=self.clear_constraints)
        self.input_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.room_input_frame = RoomInputFrame(add_room=self.add_room, clear_rooms=self.clear_rooms)
        self.room_input_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.constraint_frame = ttk.Frame(self.root)
        self.constraint_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.constraint_display = tk.Text(self.constraint_frame, height=10, width=50)
        self.constraint_display.pack(padx=5, pady=5)

        self.room_frame = ttk.Frame(self.root)
        self.room_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.room_display = tk.Text(self.room_frame, height=10, width=50)
        self.room_display.pack(padx=5, pady=5)

    def add_constraint(self, room1, room2, direction):
        self.constraint_display.insert(tk.END, f"{room1} {direction} {room2}\n")
        self.constraints.append((room1, room2, direction))

        # Add the constraint to the image drawer
        self.image_drawer.update_plot(self.constraints, new_sizes=self.sizes)

    def clear_constraints(self):
        self.constraint_display.delete(1.0, tk.END)
        self.constraints = []
        self.image_drawer.update_plot(self.constraints)

    def add_room(self, room_name, x, y):
        if room_name in self.sizes:
            return
        self.room_display.insert(tk.END, f"{room_name} {x} {y}\n")
        self.sizes[room_name] = (int(x), int(y))

        self.input_frame.update_room_list(self.sizes.keys())

    def clear_rooms(self):
        self.room_display.delete(1.0, tk.END)
        self.sizes = {}
        self.input_frame.update_room_list(self.sizes.keys())
        self.image_drawer.update_plot(self.constraints, new_sizes=self.sizes)


if __name__ == "__main__":
    root = tk.Tk()
    app = RelativeMapGUI(root)
    root.mainloop()
