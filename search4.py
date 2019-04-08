"""
COMP30024 Artificial Intelligence, Semester 1 2019
Solution to Project Part A: Searching

Authors:
"""

import sys
import json
import math

debug =True

class Exit:
    def __init__(self, data):
        self.data = data

    def exit_list(self):
        if self.data['colour'] == 'red':
            return [(3,-3), (3,-2), (3,-1), (3,0)]

        elif self.data['colour'] == 'blue':
            return [(0,-3), (-1,-2), (-2,-1), (-3,0)]

        else:
            return [(-3,3), (-2,3), (-1,3), (0,3)]

class Board:
    hexes = {}
    def __init__(self, pieces, blocks):
        self.pieces = pieces
        self.blocks = blocks

    def create_board(self, exit):
        for i in range(-3,1):
            for j in range(-3-i, 4):
                self.hexes[(i,j)] = (Hex([], (i,j), min([euc_dist((i,j), e) for e in exit])))
        for i in range(1,4):
            for j in range(-3,4-i):
                self.hexes[(i,j)] = (Hex([], (i,j), min([euc_dist((i,j), e) for e in exit])))

        all_blocks = self.blocks + [p.coordinates for p in self.pieces]
        for h in self.hexes.values():
            h.get_neighbours(self.hexes, all_blocks)

def euc_dist(me, coord):
    dist = math.sqrt((coord[0] - me[0])**2 + (coord[1] - me[1])**2)
    return dist

class Hex:
    def __init__(self, neighbours, coordinates, heuristic):
        self.neighbours = neighbours
        self.coordinates = coordinates
        self.heuristic = heuristic

    def get_neighbours(self, hexes, blocks):
        self.neighbours = []
        for i in range(-1,2):
            for j in range(-1,2):
                if i != j:
                    x, y = (self.coordinates[0] + i, self.coordinates[1] + j)
                    if (x,y) in blocks:
                        if (x+i,y+j) in hexes.keys() and (x+i, y+j) not in blocks:
                            self.neighbours.append(hexes[(x+i,y+j)])
                    elif (x,y) in hexes.keys():
                        self.neighbours.append(hexes[(x,y)])

class PriorityQueue:
    def __init__(self):
        self.elements = []
    def empty(self):
        return len(self.elements) == 0
    def put(self, x):
        self.elements.append(x)
        #self.elements = sorted(self.elements)
    def put2(self, x):
        self.elements.append(x)
        self.elements = sorted(self.elements, reverse = True)
    def get(self):
        return self.elements.pop(0)

class Piece:
    def __init__(self, coordinates, colour):
        self.coordinates = coordinates
        self.colour = colour

    def __lt__(self, other):
        return self.coordinates < other.coordinates

    def move_piece(self, board, exit):
        curr = self.coordinates
        board.pieces.remove(self)
        next_coord = next_step(curr, board, exit)
        possible_boards = []
        path_board = []
        for new in next_coord:
            if new in exit:
                if abs(new[0] - curr[0]) == 2 or abs(new[1] - curr[1]) == 2:
                    path_board.append(([f"JUMP from {curr} to {new}.", f"EXIT from {new}."], board.pieces.copy()))

                else:
                    path_board.append(([f"MOVE from {curr} to {new}.", f"EXIT from {new}."], board.pieces.copy()))
            else:
                new_piece = Piece(tuple(new), self.colour)
                board.pieces.append(new_piece)
                if abs(new[0] - curr[0]) == 2 or abs(new[1] - curr[1]) == 2:
                    path_board.append(([f"JUMP from {curr} to {new}."], board.pieces.copy()))
                else:
                    path_board.append(([f"MOVE from {curr} to {new}."], board.pieces.copy()))
                board.pieces.remove(new_piece)
        board.pieces.append(self)
        return path_board

class PathNode:
    next = []
    def __init__(self, board, cost, path, prior):
        self.board = board
        self.cost = cost
        self.path = path
        self.prior = prior

    def __lt__(self, other):
        return self.cost < other.cost

    def make_move(self, exit, furthest):
        board = self.board
        self.next = []
        for piece in board.pieces:
            piece_positions = piece.move_piece(board, exit)
            for i in piece_positions:
                self.next.append(new_board(i[1], board.blocks, exit))
                summ = sum([self.next[-1].hexes[piece.coordinates].heuristic for piece in self.next[-1].pieces])
                furthest.put2((1 + summ, PathNode(self.next[-1], 1 + summ, self.path + i[0], self)))
        return

def new_board(pieces, blocks, exit):
    board = Board(pieces, blocks)
    board.create_board(exit)
    return board

def next_step(current, board, exit):
    hexes = board.hexes
    poss = sorted([(n.heuristic, n.coordinates) for n in hexes[current].neighbours])
    poss = [p[1] for p in poss if p[0] == poss[0][0]]
    return poss

def simulate():
    pass

def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)

    exit = Exit(data)
    exit_list = exit.exit_list()

    pieces = [Piece(tuple(piece), data['colour']) for piece in data['pieces']]

    board = Board(pieces, [tuple(b) for b in data['blocks']])
    board.create_board(exit_list)

    root = PathNode(board, sum([board.hexes[piece.coordinates].heuristic for piece in board.pieces]), [], None)

    furthest = PriorityQueue()
    furthest.put2((0, root))

    while not furthest.empty():
        total, node = furthest.get()
        node.make_move(exit_list, furthest)
        if not board.pieces:
            break

    for i in node.path:
        print(i)

    # while not furthest.empty():
    #     if debug == False:
    #         dict_draw = {piece.coordinates: 'o' for piece in board.pieces}
    #         dict_draw.update({block:'XXX' for block in board.blocks})
    #         print_board(dict_draw)
    #     h, piece, path = furthest.get()
    #     a,b = piece.make_move(board, exit_list)
    #     if a == 1:
    #         furthest.put2((board.hexes[b.coordinates].heuristic, b, b.path))
    #     board.create_board(exit_list)


    # TODO: Search for and output winning sequence of moves
    # ...




def print_board(board_dict, message="", debug=True, **kwargs):
    """
    Helper function to print a drawing of a hexagonal board's contents.

    Arguments:

    * `board_dict` -- dictionary with tuples for keys and anything printable
    for values. The tuple keys are interpreted as hexagonal coordinates (using
    the axial coordinate system outlined in the project specification) and the
    values are formatted as strings and placed in the drawing at the corres-
    ponding location (only the first 5 characters of each string are used, to
    keep the drawings small). Coordinates with missing values are left blank.

    Keyword arguments:

    * `message` -- an optional message to include on the first line of the
    drawing (above the board) -- default `""` (resulting in a blank message).
    * `debug` -- for a larger board drawing that includes the coordinates
    inside each hex, set this to `True` -- default `False`.
    * Or, any other keyword arguments! They will be forwarded to `print()`.
    """

    # Set up the board template:
    if not debug:
        # Use the normal board template (smaller, not showing coordinates)
        template = """# {0}
#           .-'-._.-'-._.-'-._.-'-.
#          |{16:}|{23:}|{29:}|{34:}|
#        .-'-._.-'-._.-'-._.-'-._.-'-.
#       |{10:}|{17:}|{24:}|{30:}|{35:}|
#     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#    |{05:}|{11:}|{18:}|{25:}|{31:}|{36:}|
#  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
# |{01:}|{06:}|{12:}|{19:}|{26:}|{32:}|{37:}|
# '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#    |{02:}|{07:}|{13:}|{20:}|{27:}|{33:}|
#    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#       |{03:}|{08:}|{14:}|{21:}|{28:}|
#       '-._.-'-._.-'-._.-'-._.-'-._.-'
#          |{04:}|{09:}|{15:}|{22:}|
#          '-._.-'-._.-'-._.-'-._.-'"""
    else:
        # Use the debug board template (larger, showing coordinates)
        template = """# {0}
#              ,-' `-._,-' `-._,-' `-._,-' `-.
#             | {16:} | {23:} | {29:} | {34:} |
#             |  0,-3 |  1,-3 |  2,-3 |  3,-3 |
#          ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#         | {10:} | {17:} | {24:} | {30:} | {35:} |
#         | -1,-2 |  0,-2 |  1,-2 |  2,-2 |  3,-2 |
#      ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#     | {05:} | {11:} | {18:} | {25:} | {31:} | {36:} |
#     | -2,-1 | -1,-1 |  0,-1 |  1,-1 |  2,-1 |  3,-1 |
#  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
# | {01:} | {06:} | {12:} | {19:} | {26:} | {32:} | {37:} |
# | -3, 0 | -2, 0 | -1, 0 |  0, 0 |  1, 0 |  2, 0 |  3, 0 |
#  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#     | {02:} | {07:} | {13:} | {20:} | {27:} | {33:} |
#     | -3, 1 | -2, 1 | -1, 1 |  0, 1 |  1, 1 |  2, 1 |
#      `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#         | {03:} | {08:} | {14:} | {21:} | {28:} |
#         | -3, 2 | -2, 2 | -1, 2 |  0, 2 |  1, 2 | key:
#          `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' ,-' `-.
#             | {04:} | {09:} | {15:} | {22:} |   | input |
#             | -3, 3 | -2, 3 | -1, 3 |  0, 3 |   |  q, r |
#              `-._,-' `-._,-' `-._,-' `-._,-'     `-._,-'"""

    # prepare the provided board contents as strings, formatted to size.
    ran = range(-3, +3+1)
    cells = []
    for qr in [(q,r) for q in ran for r in ran if -q-r in ran]:
        if qr in board_dict:
            cell = str(board_dict[qr]).center(5)
        else:
            cell = "     " # 5 spaces will fill a cell
        cells.append(cell)

    # fill in the template to create the board drawing, then print!
    board = template.format(message, *cells)
    print(board, **kwargs)


# when this module is executed, run the `main` function:
if __name__ == '__main__':
    main()
