import pycosat
import argparse

class Slitherlink(object):

    # Definition of variables.
    def __init__(self):
        self.cells = None
        self.width = None
        self.height = None
        self.cell_rules = []
        self.loop_rules = []

    # Function to read in Slitherlink problem as text file.
    def read_problem(self, filename):
        with open(filename) as f:
            for line in f:
                for char in line.strip():
                    if char == '.':
                        self.cells = None
                    else:
                        self.cells = int(char)
        self.width = len(self.cells[0])
        self.height = len(self.cells)

    def encode_cell(self):
        def val_zero(e1, e2, e3, e4):
            return [[-e1], [-e2], [-e3], [-e4]]

        def val_one(e1, e2, e3, e4):
            return [[-e1, -e2], [-e1, -e3], [-e1, -e4],
                    [-e2, -e3], [-e2, -e4], [-e3, -e4],
                    [e1, e2, e3, e4]]

        def val_two(e1, e2, e3, e4):
            return [[e2, e3, e4], [e1, e3, e4],
                    [e1, e2, e4], [e1, e2, e3],
                    [-e2, -e3, -e4], [-e1, -e3, -e4],
                    [-e1, -e2, -e4], [-e1, -e2, -e3]]

        def val_three(e1, e2, e3, e4):
            return [[e1, e2], [e1, e3], [e1, e4],
                    [e2, e3], [e2, e4], [e3, e4],
                    [-e1, -e2, -e3, -e4]]

        self.cell_rules = []
        cnf_builder = [val_zero, val_one, val_two, val_three]
        cell_id = -1
        for row in range(self.height):
            for col in range(self.width):
                cell_id += 1
                cell_value = self.cells[row][col]
                assert cell_value in [None, 0, 1, 2, 3]
                if cell_value is None:
                    pass
                else:
                    assert 0 <= cell_value <= 3
                    edges = [1 + e for e in self.get_cell_edges(cell_id)]
                    clauses = cnf_builder[cell_value](*edges)
                    self.cell_rules += clauses