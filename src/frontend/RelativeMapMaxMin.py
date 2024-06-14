import io
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from constraint import Problem
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

DEBUG_MODE = True

VAR_SIDE_NUM = 0
GLOBAL_RANGE = [i for i in range(0, 5)]

# The default coordinates to show when no relative coordinates are provided
DEFAULT_COORDINATES = {
    'Default Graph': (0, 0),
}

STRICT_MODE = True


class RelativeMapMaxMin(tk.Frame):
    def __init__(self):
        super().__init__()
        self.problem = Problem()
        self.variables = []  # Store the variables
        self.sizes = {}  # Store the sizes of the variables

        self.coordinates = {}

        self.__create_widgets()

    def reset(self):
        self.problem.reset()
        self.variables = []
        self.sizes = {}
        self.coordinates = {}

    def __create_widgets(self, relative_coordinates=None):
        photo = self.draw_plot(relative_coordinates, None)
        self.label = ttk.Label(self, image=photo)
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
            ax = fig.add_subplot(1, 1, 1)
            ax.set_xlim(-1, 2)
            ax.set_ylim(-1, 2)

            ax.text(0, 0, 'Default Graph', fontsize=12, ha='center', va='center')

        else:
            # If the relative coordinates are provided,
            # transform into csp problem and solve it
            self.load_coordinates(relative_coordinates, sizes)
            solutions = self.problem.getSolutions()
            solution = solutions[0]
            print(solutions)
            for v in self.variables:
                self.coordinates[v] = (solution[v + '_x'], solution[v + '_y'])

            ax = fig.add_subplot(1, 1, 1)
            ax.set_xlim(min(x for x, _ in self.coordinates.values()) - 1,
                        max(x for x, _ in self.coordinates.values()) + 2)
            ax.set_ylim(min(y for _, y in self.coordinates.values()) - 1,
                        max(y for _, y in self.coordinates.values()) + 2)

            backward_dict = {v: k for k, v in self.coordinates.items()}

            # Iterate over the backward dict to draw the lines
            for (x, y), label in backward_dict.items():
                # Draw the squares using the coordinates and sizes
                ax.plot([x, x + self.sizes[label][1], x + self.sizes[label][1], x, x],
                        [y, y, y + self.sizes[label][0], y + self.sizes[label][0], y], 'k-')
                ax.text(x + 0.5 * self.sizes[label][1], y + 0.5 * self.sizes[label][0], label, fontsize=12, ha='center',
                        va='center')

            ax.axis('on')

        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        img = Image.open(buf)
        photo = ImageTk.PhotoImage(img)

        return photo

    def load_coordinate_single(self, coord, height, width):
        if (coord in self.variables):
            return

        self.problem.addVariable(coord + '_x', GLOBAL_RANGE)
        self.problem.addVariable(coord + '_y', GLOBAL_RANGE)
        self.variables.append(coord)

        self.sizes[coord] = (height, width)

    def load_coordinates(self, coordinates, sizes=None):
        # Store the coordinates and sizes
        if sizes is not None:
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
            if z == 'west':
                self.add_to_left_single(x, y)
            elif z == 'east':
                self.add_to_right_single(x, y)
            elif z == 'north':
                self.add_to_top_single(x, y)
            elif z == 'south':
                self.add_to_bottom_single(x, y)

        self.set_all_variables_not_same()

    def add_to_left_single(self, x, y):
        self.problem.addConstraint(lambda x_x, y_x: x_x > y_x, (x + '_x', y + '_x'))
        self.problem.addConstraint(lambda x_y, y_y: (x_y + self.sizes[x][0] > y_y >= x_y) or (
                y_y + self.sizes[y][0] > x_y >= y_y),
                                   (x + '_y', y + '_y'))

        # Strict position
        if STRICT_MODE:
            self.problem.addConstraint(lambda x_x, y_x: x_x == y_x + self.sizes[y][1], (x + '_x', y + '_x'))

    def add_to_right_single(self, x, y):

        self.problem.addConstraint(lambda x_x, y_x: x_x < y_x, (x + '_x', y + '_x'))
        self.problem.addConstraint(lambda x_y, y_y: (x_y + self.sizes[x][0] > y_y >= x_y) or (
                y_y + self.sizes[y][0] > x_y >= y_y),
                                   (x + '_y', y + '_y'))

        # Strict position
        if STRICT_MODE:
            self.problem.addConstraint(lambda x_x, y_x: y_x == x_x + self.sizes[x][1], (x + '_x', y + '_x'))

    def add_to_top_single(self, x, y):
        self.problem.addConstraint(lambda x_y, y_y: x_y < y_y, (x + '_y', y + '_y'))
        self.problem.addConstraint(lambda x_x, y_x: (x_x + self.sizes[x][1] > y_x >= x_x) or (
                y_x + self.sizes[y][1] > x_x >= y_x),
                                   (x + '_x', y + '_x'))

        # Strict position
        if STRICT_MODE:
            self.problem.addConstraint(lambda x_y, y_y: y_y == x_y + self.sizes[x][0], (x + '_y', y + '_y'))

    def add_to_bottom_single(self, x, y):
        self.problem.addConstraint(lambda x_y, y_y: x_y > y_y, (x + '_y', y + '_y'))
        self.problem.addConstraint(lambda x_x, y_x: (x_x + self.sizes[x][1] > y_x >= x_x) or (
                y_x + self.sizes[y][1] > x_x >= y_x),
                                   (x + '_x', y + '_x'))

        # Strict position
        if STRICT_MODE:
            self.problem.addConstraint(lambda x_y, y_y: x_y == y_y + self.sizes[y][0], (x + '_y', y + '_y'))

    def set_to_initial(self, x):
        self.problem.addConstraint(lambda x_x, x_y: x_x == 0 and x_y == 0, (x + '_x', x + '_y'))

    def set_two_variables_not_same(self, x, y):
        # add constraint that the area of two rooms cannot overlap
        self.problem.addConstraint(
            lambda x_x, y_x, x_y, y_y:
            not (
                    y_x + self.sizes[y][1] > x_x >= y_x or x_x + self.sizes[x][1] > y_x >= x_x
            ) or not
            (y_y + self.sizes[y][0] > x_y >= y_y or x_y + self.sizes[x][0] > y_y >= x_y),
            (x + '_x', y + '_x', x + '_y', y + '_y')

        )

    def set_all_variables_not_same(self):
        for i in range(len(self.variables)):
            for j in range(i + 1, len(self.variables)):
                self.set_two_variables_not_same(self.variables[i], self.variables[j])

    def update_plot(self, new_relative_coordinates, new_sizes=None):
        self.reset()

        photo = self.draw_plot(new_relative_coordinates, new_sizes)
        self.label.config(image=photo)
        self.label.image = photo
