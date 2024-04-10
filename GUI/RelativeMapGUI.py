import tkinter as tk

from GUI.RelativeMap import RelativeMap

class RelativeInput(tk.Frame):
    def __init__(self, rooms, add_constraint, clear_constraints):
        super().__init__()
        self.rooms = rooms
        self.add_constraint = add_constraint
        self.clear_constraints = clear_constraints

        self.room1 = tk.StringVar()
        self.room2 = tk.StringVar()
        self.direction = tk.StringVar()
        self.room1.set("Room 1")
        self.room2.set("Room 2")
        self.direction.set("Direction")

        self.room1_drop = tk.OptionMenu(self, self.room1, "None", *self.rooms)
        self.room2_drop = tk.OptionMenu(self, self.room2,"None", *self.rooms)
        self.direction_drop = tk.OptionMenu(self, self.direction, "left", "right", "top", "bottom")
        self.room1_drop.pack(side=tk.LEFT)
        self.room2_drop.pack(side=tk.LEFT)
        self.direction_drop.pack(side=tk.LEFT)

        self.add_constraint_button = tk.Button(self, text="Add Constraint", command=self.local_add_constraint)
        self.add_constraint_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(self, text="Clear Constraints", command=self.clear_constraints)
        self.clear_button.pack(side=tk.LEFT)


    def local_add_constraint(self):
        room1 = self.room1.get()
        room2 = self.room2.get()
        direction = self.direction.get()

        self.add_constraint(room1, room2, direction)

    def update_room_list(self, rooms):
        self.rooms = rooms
        self.room1_drop['menu'].delete(0, 'end')
        self.room2_drop['menu'].delete(0, 'end')
        for room in self.rooms:
            self.room1_drop['menu'].add_command(label=room,
                                                command=lambda room=room: self.room1.set(room))
            self.room2_drop['menu'].add_command(label=room,
                                                command=lambda room=room: self.room2.set(room))

class RoomInput(tk.Frame):
    def __init__(self, add_room, clear_rooms):
        super().__init__()
        self.add_room = add_room
        self.clear_rooms = clear_rooms

        self.room_name = tk.StringVar(self)
        self.height = tk.StringVar(self)
        self.width = tk.StringVar(self)
        self.room_name_input = tk.Entry(self, textvariable=self.room_name)
        self.room_x_input = tk.Entry(self, textvariable=self.height)
        self.room_y_input = tk.Entry(self, textvariable=self.width)
        self.room_name_input.pack(side=tk.LEFT)
        self.room_x_input.pack(side=tk.LEFT)
        self.room_y_input.pack(side=tk.LEFT)
        self.add_room_button = tk.Button(self, text="Add Room", command=self.local_add_room)
        self.add_room_button.pack(side=tk.LEFT)
        self.clear_button = tk.Button(self, text="Clear Rooms", command=self.clear_rooms)
        self.clear_button.pack(side=tk.LEFT)

    def local_add_room(self):
        room_name = self.room_name.get()
        height = self.height.get()
        width = self.width.get()
        self.add_room(room_name, height, width)



class RelativeMapGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Relatvie Map GUI")
        self.constraints = []
        self.sizes = {}

        self.image_drawer = RelativeMap()
        self.image_drawer.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Create a frame for the input
        self.input_frame = RelativeInput(rooms=self.sizes.keys(), add_constraint=self.add_constraint, clear_constraints=self.clear_constraints)
        self.input_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.room_input_frame = RoomInput(add_room=self.add_room, clear_rooms=self.clear_rooms)
        self.room_input_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add a text display for the constraints
        self.constraint_display = tk.Text(self.root, height=10, width=50)
        self.constraint_display.pack(side=tk.LEFT)

        self.room_display = tk.Text(self.root, height=10, width=50)
        self.room_display.pack(side=tk.LEFT)

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
