import time
import pycosat
import multiprocessing


class Slitherlink(object):

    # Definition of some important variables
    def __init__(self):
        self.cells = None
        self.width = None
        self.height = None
        self.cell_constraints = []
        self.loop_constraints = []

    """"
     TODO
     Rewrite read problem function 
    """

    def read_problem(self, filename):
        with open(filename) as fin:
            self.cells = [[None if char == '.' else int(char)
                           for char in line.strip()]
                          for line in fin]
        self.width = len(self.cells[0])
        self.height = len(self.cells)

    def get_cell_edges(self, cell_id):
        # Define the position of a cell by its id
        cell_row = cell_id // self.width
        cell_col = cell_id % self.height
        num_horizontal = self.height * (self.width + 1)
        # Return four integers
        upper_edge = cell_id
        lower_edge = upper_edge + self.width
        left_edge = num_horizontal + ((cell_row * (self.width + 1)) + cell_col)
        right_edge = left_edge + 1
        return [upper_edge, lower_edge, left_edge, right_edge]

    def get_corner_vertexes(self, vertex_id):
        col = vertex_id % (self.width + 1)
        row = vertex_id // (self.width + 1)
        upper_edge = None
        lower_edge = None
        left_edge = None
        right_edge = None
        distance = self.width * (self.height + 1)
        if row > 0:
            upper_edge = distance + vertex_id - (self.width + 1)
        if row < self.height:
            lower_edge = distance + vertex_id
        if col > 0:
            left_edge = (self.width * row) + col - 1
        if col < self.width:
            right_edge = (self.width * row) + col
        vertexes = [vertex for vertex in [upper_edge, lower_edge, left_edge, right_edge]
                    if vertex is not None]
        return vertexes

    def get_adjacent_edges(self, edge_id):
        num_vertexes = (self.width + 1) * (self.height + 1)
        v1, v2 = [vertex_id for vertex_id in range(num_vertexes)
                  if edge_id in self.get_corner_vertexes(vertex_id)]
        edge1 = [edge for edge in self.get_corner_vertexes(v1)
                 if edge != edge_id]
        edge2 = [edge for edge in self.get_corner_vertexes(v2)
                 if edge != edge_id]
        return edge1 + edge2

    def generate_cell_constraints(self):

        # If the value of the cell is 0
        def zero(e1, e2, e3, e4):
            return [[-e1], [-e2], [-e3], [-e4]]

        # If the value of the cell is 1
        def one(e1, e2, e3, e4):
            return [[e1, e2, e3, e4], [-e1, -e2], [-e1, -e3], [-e1, -e4],
                    [-e2, -e3], [-e2, -e4], [-e3, -e4]]

        # If the value of the cell is 2
        def two(e1, e2, e3, e4):
            return [[e2, e3, e4], [e1, e3, e4],
                    [e1, e2, e4], [e1, e2, e3],
                    [-e2, -e3, -e4], [-e1, -e3, -e4],
                    [-e1, -e2, -e4], [-e1, -e2, -e3]]

        # If the value of the cell is 3
        def three(e1, e2, e3, e4):
            return [[e1, e2], [e1, e3], [e1, e4],
                    [e2, e3], [e2, e4], [e3, e4],
                    [-e1, -e2, -e3, -e4]]

        self.cell_constraints = []
        # Base value of cell_id
        cell_id = -1
        list_value = [zero, one, two, three]
        for row in range(self.width):
            for col in range(self.height):
                cell_id += 1
                cell_value = self.cells[row][col]
                if cell_value is None:
                    pass
                else:
                    edges = [1 + e for e in self.get_cell_edges(cell_id)]
                    clause = list_value[cell_value](*edges)
                    self.cell_constraints += clause

    def generate_loop_constraints(self):

        # Number of correct edges if a vertex is in the corner
        def two(e1, e2):
            return [[-e1, e2], [e1, -e2]]

        # Number of correct edges if a vertex is in the edge
        def three(e1, e2, e3):
            return [[-e1, e2, e3],
                    [e1, -e2, e3],
                    [e1, e2, -e3],
                    [-e1, -e2, -e3]]

        # Number of correct edges if a vertex is inside the board
        def four(e1, e2, e3, e4):
            return [[-e1, e2, e3, e4],
                    [e1, -e2, e3, e4],
                    [e1, e2, -e3, e4],
                    [e1, e2, e3, -e4],
                    [-e1, -e2, -e3],
                    [-e1, -e2, -e4],
                    [-e1, -e3, -e4],
                    [-e2, -e3, -e4]]

        corner_vertexes = (self.width + 1) * (self.height + 1)
        vertex_constraints = [None, None, two, three, four]
        for vertex_id in range(corner_vertexes):
            vertexes = [1 + e for e in self.get_corner_vertexes(vertex_id)]
            clause = vertex_constraints[len(vertexes)](*vertexes)
            self.loop_constraints += clause

    def call_sat_solver(self):
        constraints = self.cell_constraints + self.loop_constraints
        # Print number of clauses
        numclause = len(constraints)
        print("Number of clauses: " + str(numclause))
        for solution in pycosat.itersolve(constraints):
            test_solution = [edge for edge in solution if edge > 0]
            result = self.is_one_loop(test_solution)
            if result:
                self.solution = test_solution
                break

    # Check if there is only a single loop
    def is_one_loop(self, solution):
        if solution is []:
            return False
        solution = [edge - 1 for edge in solution]
        far_edges = solution[1:]
        start = [solution[0]]
        # Implement Fill Algorithm
        while far_edges != []:
            lines = [line for edge in start
                     for line in self.get_adjacent_edges(edge)
                     if line in far_edges]
            if lines == [] and far_edges != []:
                return False
            far_edges = [edge for edge in far_edges if edge not in lines]
            start = lines
        return True

    def solve(self):
        # Receive problem and take solution
        # start time
        start = time.time()
        self.read_problem("test/1515hard.txt")
        self.generate_cell_constraints()
        self.generate_loop_constraints()
        self.call_sat_solver()
        self.draw_solution()
        # end time
        end = time.time()
        print("Total time: " + str(end - start))

    def draw_solution(self):
        num_row = 4 * (self.height + 1) + 1
        num_col = 4 * (self.width + 1) + 1
        g = [[' ' for cols in range(num_col)] for rows in range(num_row)]

        def horizontal_edge(edge):
            col_f = edge % self.width
            row_l = edge // self.width
            y = 4 * row_l
            x1 = 4 * col_f
            x2 = 4 * (col_f + 1)
            for x in range(x1, x2 + 1):
                g[y][x] = '#'

        def vertical_edge(edge):
            row_f = edge // (self.width + 1)
            col_l = edge % (self.width + 1)
            y1 = 4 * row_f
            y2 = 4 * (row_f + 1)
            x = 4 * col_l
            for y in range(y1, y2 + 1):
                g[y][x] = '#'

        def draw_numbers():
            for row_index, row in enumerate(self.cells):
                for col_index, val in enumerate(row):
                    if val is not None:
                        y = 4 * row_index + 2
                        x = 4 * col_index + 2
                        g[y][x] = str(val)

        draw_numbers()
        horizontal_limit = self.height * (self.width + 1)
        horizontals = [e - 1
                       for e in self.solution
                       if e <= horizontal_limit]
        verticals = [e - horizontal_limit - 1
                     for e in self.solution
                     if e > horizontal_limit]
        for h_edge in horizontals:
            horizontal_edge(edge=h_edge)
        for v_edge in verticals:
            vertical_edge(edge=v_edge)
        gs = '\n'.join([''.join(g_row) for g_row in g])
        print(gs)


if __name__ == '__main__':
    slither = Slitherlink()
    p = multiprocessing.Process(target=slither.solve)
    p.start()
    p.join(600)
    if p.is_alive():
        print("Process timeout after 10 minutes")
        p.kill()
        p.join()
