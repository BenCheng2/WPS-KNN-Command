import io
import tkinter as tk
from PIL import Image, ImageTk
from constraint import Problem
from constraint import FunctionConstraint
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

DEBUG_MODE = True

VAR_SIDE_NUM = 0
GLOBAL_RANGE = [i for i in range(-5, 5)]

# The default coordinates to show when no relative coordinates are provided
DEFAULT_COORDINATES = {
    'Default Graph': (0, 0),
}

A_x_vars = []
B_x_vars = []
A_y_vars = []
B_y_vars = []

RESTRICT_LEVEL = "any" # there are bugs when using "all


def constraint_add_any_to_left(*args):
    B_positions = args[:len(B_x_vars)]
    A_positions = args[len(B_x_vars):]
    return any(b < a for b in B_positions for a in A_positions)

def constraint_add_any_to_right(*args):
    B_positions = args[:len(B_x_vars)]
    A_positions = args[len(B_x_vars):]
    return any(b > a for b in B_positions for a in A_positions)

def constraint_add_any_to_top(*args):
    B_positions = args[:len(B_y_vars)]
    A_positions = args[len(B_y_vars):]
    return any(b > a for b in B_positions for a in A_positions)

def constraint_add_any_to_bottom(*args):
    B_positions = args[:len(B_y_vars)]
    A_positions = args[len(B_y_vars):]
    if RESTRICT_LEVEL == "any":
        return any(b < a for b in B_positions for a in A_positions)
    else:
        return max(B_positions) < min(A_positions)

def constraint_remain_any_to_horizontal(*args):
    B_positions = args[:len(B_y_vars)]
    A_positions = args[len(B_y_vars):]
    return any(b == a for b in B_positions for a in A_positions)

def constraint_remain_any_to_vertical(*args):
    B_positions = args[:len(B_x_vars)]
    A_positions = args[len(B_x_vars):]
    return any(b == a for b in B_positions for a in A_positions)


class RelativeMap(tk.Frame):
    def __init__(self):
        super().__init__()
        self.problem = Problem()
        self.variables = {}  # Store the variables to ensure no repeated variables, store the basic name and all the sub coordinates
        self.coordinates = {}
        self.sizes = {}  # Store the sizes of the variables
        self.__create_widgets(
            [('A', 'B', 'top'), ('A', 'C', 'top')])

    def reset(self):
        self.problem.reset()
        self.variables = {}
        self.coordinates = {}

    def __create_widgets(self, relative_coordinates=None):
        photo = self.draw_plot(relative_coordinates, None)
        self.label = tk.Label(self, image=photo)
        self.label.image = photo
        self.label.pack()

    def draw_plot(self, relative_coordinates=None, sizes=None):
        """
        Draw the plot based on the relative coordinates
        Only process the image generation, not the display
        :param relative_coordinates: the relative coordinates to draw the plot
        :return: A photo of the plot
        """
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(fig)

        if relative_coordinates is None or len(relative_coordinates) == 0:
            # If no relative coordinates are provided, show the default coordinates
            self.coordinates = DEFAULT_COORDINATES
        else:
            # If the relative coordinates are provided,
            # transform into csp problem and solve it
            self.load_coordinates(relative_coordinates, sizes)
            solutions = self.problem.getSolutions()
            solution = solutions[0]
            for v in self.variables:
                for subcoord in self.variables[v]:
                    self.coordinates[subcoord] = (solution[subcoord + '_x'], solution[subcoord + '_y'])

        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlim(min(x for x, _ in self.coordinates.values()) - 1,
                    max(x for x, _ in self.coordinates.values()) + 2)
        ax.set_ylim(min(y for _, y in self.coordinates.values()) - 1,
                    max(y for _, y in self.coordinates.values()) + 2)

        backward_dict = {v: k for k, v in self.coordinates.items()}

        # Iterate over the backward dict to draw the lines
        for (x, y), label in backward_dict.items():
            if (x - 1, y) not in backward_dict:
                ax.plot([x, x], [y, y + 1], 'k-')
            if (x + 1, y) not in backward_dict:
                ax.plot([x + 1, x + 1], [y, y + 1], 'k-')
            if (x, y + 1) not in backward_dict:
                ax.plot([x, x + 1], [y + 1, y + 1], 'k-')
            if (x, y - 1) not in backward_dict:
                ax.plot([x, x + 1], [y, y ], 'k-')

            # if the left room is in the dict, but not the same label
            if (x - 1, y) in backward_dict and (backward_dict[(x - 1, y)] and backward_dict[(x - 1, y)] != label and backward_dict[(x - 1, y)][0] != label[0]):
                ax.plot([x, x], [y, y + 1], 'k-')
            # if the right room is in the dict, but not the same label
            if (x + 1, y) in backward_dict and (backward_dict[(x + 1, y)] and backward_dict[(x + 1, y)] != label and backward_dict[(x + 1, y)][0] != label[0]):
                ax.plot([x + 1, x + 1], [y, y + 1], 'k-')
            # if the top room is in the dict, but not the same label
            if (x, y + 1) in backward_dict and (backward_dict[(x, y + 1)] and backward_dict[(x, y + 1)] != label and backward_dict[(x, y + 1)][0] != label[0]):
                ax.plot([x, x + 1], [y + 1, y + 1], 'k-')
            # if the bottom room is in the dict, but not the same label
            if (x, y - 1) in backward_dict and (backward_dict[(x, y - 1)] and backward_dict[(x, y - 1)] != label and backward_dict[(x, y - 1)][0] != label[0]):
                ax.plot([x, x + 1], [y, y], 'k-')

            ax.text(x + 0.5, y + 0.5, label, ha='center', va='center')

        ax.axis('off')

        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        img = Image.open(buf)
        photo = ImageTk.PhotoImage(img)

        return photo


    def load_coordinate_single(self, coord, height, width):
        if (coord in self.variables):
            return

        if height == 1 and width == 1:
            self.problem.addVariable(coord + '_x', GLOBAL_RANGE)
            self.problem.addVariable(coord + '_y', GLOBAL_RANGE)

            self.variables[coord] = [coord]

        else:
            self.variables[coord] = []
            # Add the variables for the height and width
            for i in range(width):
                for j in range(height):
                    self.problem.addVariable(coord + str(i) + str(j) + '_x', GLOBAL_RANGE)
                    self.problem.addVariable(coord + str(i) + str(j) + '_y', GLOBAL_RANGE)
                    self.variables[coord].append(coord + str(i) + str(j))

            # Add the constraints for the height and width
            for i in range(width):
                for j in range(height):

                    if j < height - 1:
                        first_x = coord + str(i) + str(j) + '_x'
                        first_y = coord + str(i) + str(j) + '_y'
                        second_x = coord + str(i) + str(j + 1) + '_x'
                        second_y = coord + str(i) + str(j + 1) + '_y'

                        self.problem.addConstraint(lambda x, y: x + 1 == y,
                                                   (first_y, second_y))
                        self.problem.addConstraint(lambda x, y: x == y,
                                                   (first_x, second_x))

            for i in range(height):
                for j in range(width):
                    if j < width - 1:
                        first_x = coord + str(j) + str(i) + '_x'
                        first_y = coord + str(j) + str(i) + '_y'
                        second_x = coord + str(j + 1) + str(i) + '_x'
                        second_y = coord + str(j + 1) + str(i) + '_y'

                        self.problem.addConstraint(lambda x, y: x + 1 == y,
                                                   (first_x, second_x))
                        self.problem.addConstraint(lambda x, y: x == y,
                                                   (first_y, second_y))


    def load_coordinates(self, coordinates, sizes=None):
        # Store the coordinates and sizes
        self.sizes = sizes

        for (x, y, z) in coordinates:
            if sizes is not None and x in sizes:
                self.load_coordinate_single(x, sizes[x][0], sizes[x][1])
            else:
                self.load_coordinate_single(x, 1, 1)
            if sizes is not None and y in sizes:
                self.load_coordinate_single(y, sizes[y][0], sizes[y][1])
            else:
                self.load_coordinate_single(y, 1, 1)

        # add the constraints
        for (x, y, z) in coordinates:
            if z == 'left':
                self.add_to_left_single(x, y)
            elif z == 'right':
                self.add_to_right_single(x, y)
            elif z == 'top':
                self.add_to_top_single(x, y)
            elif z == 'bottom':
                self.add_to_bottom_single(x, y)

        self.set_all_variables_not_same()

    def add_to_left_single(self, x, y):
        global A_x_vars
        global B_x_vars
        global A_y_vars
        global B_y_vars

        A_x_vars = [local_x + '_x' for local_x in self.variables[x]]
        B_x_vars = [local_y + '_x' for local_y in self.variables[y]]
        self.problem.addConstraint(constraint_add_any_to_left, B_x_vars + A_x_vars)

        A_y_vars = [local_x + '_y' for local_x in self.variables[x]]
        B_y_vars = [local_y + '_y' for local_y in self.variables[y]]
        self.problem.addConstraint(constraint_remain_any_to_horizontal, B_y_vars + A_y_vars)

    def add_to_right_single(self, x, y):
        global A_x_vars
        global B_x_vars
        global A_y_vars
        global B_y_vars

        A_x_vars = [local_x + '_x' for local_x in self.variables[x]]
        B_x_vars = [local_y + '_x' for local_y in self.variables[y]]
        self.problem.addConstraint(constraint_add_any_to_right, B_x_vars + A_x_vars)

        A_y_vars = [local_x + '_y' for local_x in self.variables[x]]
        B_y_vars = [local_y + '_y' for local_y in self.variables[y]]
        self.problem.addConstraint(constraint_remain_any_to_horizontal, B_y_vars + A_y_vars)


    def add_to_top_single(self, x, y):
        global A_x_vars
        global B_x_vars
        global A_y_vars
        global B_y_vars

        A_x_vars = [local_x + '_x' for local_x in self.variables[x]]
        B_x_vars = [local_y + '_x' for local_y in self.variables[y]]
        self.problem.addConstraint(constraint_remain_any_to_vertical, B_x_vars + A_x_vars)

        A_y_vars = [local_x + '_y' for local_x in self.variables[x]]
        B_y_vars = [local_y + '_y' for local_y in self.variables[y]]
        self.problem.addConstraint(constraint_add_any_to_top, B_y_vars + A_y_vars)

    def add_to_bottom_single(self, x, y):
        global A_x_vars
        global B_x_vars
        global A_y_vars
        global B_y_vars

        A_x_vars = [local_x + '_x' for local_x in self.variables[x]]
        B_x_vars = [local_y + '_x' for local_y in self.variables[y]]
        self.problem.addConstraint(constraint_remain_any_to_vertical, B_x_vars + A_x_vars)

        A_y_vars = [local_x + '_y' for local_x in self.variables[x]]
        B_y_vars = [local_y + '_y' for local_y in self.variables[y]]
        self.problem.addConstraint(constraint_add_any_to_bottom, B_y_vars + A_y_vars)

    def set_to_initial(self, x):
        self.problem.addConstraint(lambda x_x, x_y: x_x == 0 and x_y == 0, (x + '_x', x + '_y'))

    def set_two_variables_not_same(self, x, y):
        self.problem.addConstraint(lambda x_x, y_x, x_y, y_y: x_x != y_x or x_y != y_y,
                                   (x + '_x', y + '_x', x + '_y', y + '_y'))

    def set_all_variables_not_same(self):
        real_all_vars = []
        # iterate over all the variables' subcoordinates
        for v in self.variables:
            for subcoord in self.variables[v]:
                real_all_vars.append(subcoord)

        for i in range(len(real_all_vars)):
            for j in range(i + 1, len(real_all_vars)):
                self.set_two_variables_not_same(real_all_vars[i], real_all_vars[j])

    def update_plot(self, new_relative_coordinates, new_sizes=None):
        self.reset()

        photo = self.draw_plot(new_relative_coordinates, new_sizes)
        self.label.config(image=photo)
        self.label.image = photo

# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("Tkinter Application with Embedded Matplotlib Plot")
#
#     app = RelativeMap()
#     app.pack(side="top", fill="both", expand=True)
#
#     root.mainloop()
