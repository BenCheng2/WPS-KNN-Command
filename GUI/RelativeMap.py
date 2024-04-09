import io
import tkinter as tk
from PIL import Image, ImageTk
from constraint import Problem
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

DEBUG_MODE = True

VAR_SIDE_NUM = 0
GLOBAL_RANGE = [i for i in range(-5, 5)]

# The default coordinates to show when no relative coordinates are provided
DEFAULT_COORDINATES = {
    'A': (0, 0),
    'B': (1, 0),
    'C': (2, 0),
    'D': (3, 0),
    'E': (4, 0),
    'F': (2, -1),
    'G': (4, 1),
    'H': (1, 1),
    'I': (4, -1)
}


class RelativeMap(tk.Frame):
    def __init__(self):
        super().__init__()
        self.problem = Problem()
        self.variables = []
        self.coordinates = {}
        self.__create_widgets(
            [('A', 'B', 'top'), ('A', 'C', 'top')])

    def __create_widgets(self, relative_coordinates=None):
        photo = self.draw_plot(relative_coordinates)
        self.label = tk.Label(self, image=photo)
        self.label.image = photo
        self.label.pack()

    def draw_plot(self, relative_coordinates=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(1, 1, 1)

        if relative_coordinates is None:
            self.coordinates = DEFAULT_COORDINATES
        else:
            self.load_coordinates(relative_coordinates)

            solutions = self.problem.getSolution()

            for v in self.variables:
                self.coordinates[v] = (solutions[v + '_x'], solutions[v + '_y'])

        ax.set_xlim(min(x for x, _ in self.coordinates.values()) - 1,
                    max(x for x, _ in self.coordinates.values()) + 2)
        ax.set_ylim(min(y for _, y in self.coordinates.values()) - 1,
                    max(y for _, y in self.coordinates.values()) + 2)

        # Draw squares at specified coordinates
        for label, (x, y) in self.coordinates.items():
            ax.plot([x, x + 1, x + 1, x, x], [y, y, y + 1, y + 1, y], 'k-')  # draw a square
            ax.text(x + 0.5, y + 0.5, label, ha='center', va='center')  # label each square

        ax.axis('off')

        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        img = Image.open(buf)
        photo = ImageTk.PhotoImage(img)

        return photo

    def load_coordinates(self, coordinates):
        for (x, y, z) in coordinates:
            if x not in self.variables:
                self.variables.append(x)
            if y not in self.variables:
                self.variables.append(y)
        for v in self.variables:
            self.problem.addVariable(v + '_x', GLOBAL_RANGE)
            self.problem.addVariable(v + '_y', GLOBAL_RANGE)

        # add the constraints
        for (x, y, z) in coordinates:
            if z == 'left':
                self.add_to_left(x, y)
            elif z == 'right':
                self.add_to_right(x, y)
            elif z == 'top':
                self.add_to_top(x, y)
            elif z == 'bottom':
                self.add_to_bottom(x, y)

        self.set_all_variables_not_same()

    def add_to_left(self, x, y):
        self.problem.addConstraint(lambda x_x, y_x: y_x < x_x, (x + '_x', y + '_x'))

        self.problem.addConstraint(lambda x_y, y_y: abs(x_y - y_y) <= VAR_SIDE_NUM, (x + '_y', y + '_y'))

    def add_to_right(self, x, y):
        self.problem.addConstraint(lambda x_x, y_x: x_x < y_x, (x + '_x', y + '_x'))
        self.problem.addConstraint(lambda x_y, y_y: abs(x_y - y_y) <= VAR_SIDE_NUM, (x + '_y', y + '_y'))

    def add_to_top(self, x, y):
        self.problem.addConstraint(lambda x_y, y_y: x_y < y_y, (x + '_y', y + '_y'))
        self.problem.addConstraint(lambda x_x, y_x: abs(x_x - y_x) <= VAR_SIDE_NUM, (x + '_x', y + '_x'))

    def add_to_bottom(self, x, y):
        self.problem.addConstraint(lambda x_y, y_y: x_y > y_y, (x + '_y', y + '_y'))
        self.problem.addConstraint(lambda x_x, y_x: abs(x_x - y_x) <= VAR_SIDE_NUM, (x + '_x', y + '_x'))

    def set_to_initial(self, x):
        self.problem.addConstraint(lambda x_x, x_y: x_x == 0 and x_y == 0, (x + '_x', x + '_y'))

    def set_two_variables_not_same(self, x, y):
        self.problem.addConstraint(lambda x_x, y_x, x_y, y_y: x_x != y_x or x_y != y_y,
                              (x + '_x', y + '_x', x + '_y', y + '_y'))

    def set_all_variables_not_same(self):
        for i in range(len(self.variables)):
            for j in range(i + 1, len(self.variables)):
                self.set_two_variables_not_same(self.variables[i], self.variables[j])

    def update_plot(self, new_relative_coordinates):
        self.problem.reset()
        self.variables = []
        self.coordinates = {}

        photo = self.draw_plot(new_relative_coordinates)
        self.label.config(image=photo)
        self.label.image = photo


        self.label.configure(image=photo)
        self.label.image = photo


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tkinter Application with Embedded Matplotlib Plot")

    app = RelativeMap()
    app.pack(side="top", fill="both", expand=True)

    root.mainloop()
