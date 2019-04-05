"""
COMP30024 Artificial Intelligence, Semester 1 2019
Solution to Project Part A: Searching

Authors:
"""

import sys
import json

class Piece:
    def __init__(self, colour, coordinates):
        self.colour = colour
        self.coordinates = coordinates


class Hex:
    def __init__(self, cost, neighbours, colour, coordinates):
        self.cost = cost
        self.neighbours = neighbours
        self.colour = colour
        self.coordinates = coordinates

    def new_print(self):
        printlist = []
        for n in self.neighbours:
            printlist.append(n.coordinates)
        print(printlist)

def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)

    board = {}
    exit = assign_piece_cost(board, data)

    pieces = [tuple(piece) for piece in data['pieces']]
    multi_search(board, data, exit)


def add_hexes(board, data):
    for i in range(-3,1):
        for j in range(-3-i, 4):
            board[(i,j)] = Hex([1000], [], 'white', (i,j))
    for i in range(1,4):
        for j in range(-3,4-i):
            board[(i,j)] = Hex([1000], [], 'white', (i,j))

    for block in data['pieces']:
        board[tuple(block)].colour = data['colour']

    for block in data['blocks']:
        board[tuple(block)].colour = 'black'

    for k,v in board.items():
        for i in range(-1,2):
            for j in range(-1,2):
                new_coord = (k[0]+i,k[1]+j)
                if i != j and new_coord in board:
                    if board[k].colour == 'white':
                        if board[new_coord].colour != 'black':
                            v.neighbours.append(board[new_coord])
                        elif (new_coord[0] + i, new_coord[1] + j) in board and board[(new_coord[0] + i, new_coord[1] + j)].colour != 'black':
                            v.neighbours.append(board[(new_coord[0] + i, new_coord[1] + j)])
                    elif board[k].colour in ('red', 'green', 'blue'):
                        if board[new_coord].colour == 'white':
                            v.neighbours.append(board[new_coord])
                        elif (new_coord[0] + i, new_coord[1] + j) in board and board[(new_coord[0] + i, new_coord[1] + j)].colour == 'white':
                            v.neighbours.append(board[(new_coord[0] + i, new_coord[1] + j)])

def exit_list(board, data):
    if data['colour'] == 'red':
        exit = [(3,-3), (3,-2), (3,-1), (3,0)]
        for i in exit:
            if board[i].colour != 'black':
                board[i].cost[0] = 1

    elif data['colour'] == 'blue':
        exit = [(0,-3), (-1,-2), (-2,-1), (-3,0)]
        for i in exit:
            if board[i].colour != 'black':
                board[i].cost[0] = 1

    else:
        exit = [(-3,3), (-2,3), (-1,3), (0,3)]
        for i in exit:
            if board[i].colour != 'black':
                board[i].cost[0] = 1
    return exit

def assign_cost(board, queue, pieces):
    new_pieces = []
    for i in pieces:
        new_pieces.append(tuple(i))
    while queue != []:
        curr = board[queue.pop(0)]
        for i in curr.neighbours:
            if i.cost[0] > (curr.cost[0] + 1):
                i.cost[0] = curr.cost[0] + 1
                queue.append(i.coordinates)

    for n_p in range(len(new_pieces)):
        queue = [new_pieces[n_p]]
        for i in range(-3,1):
            for j in range(-3-i, 4):
                board[(i,j)].cost.append(1000)
        for i in range(1,4):
            for j in range(-3,4-i):
                board[(i,j)].cost.append(1000)

        board[new_pieces[n_p]].cost[n_p +1] = 0
        while queue != []:
            curr = board[queue.pop(0)]
            for now in curr.neighbours:
                if now.cost[n_p+1] > (curr.cost[n_p+1] + 1):
                    now.cost[n_p+1] = curr.cost[n_p+1] + 1
                    queue.append(now.coordinates)

def assign_piece_cost(board, data):
    add_hexes(board, data)
    exit = exit_list(board, data)
    exit_copy = exit[:]
    assign_cost(board, exit, data['pieces'])
    return exit_copy

def single_move(board, coordinate, data, exit):
    neighbours = [n.coordinates for n in board[coordinate].neighbours]
    data['pieces'].remove(list(coordinate))
    board[coordinate].colour = 'white'
    if coordinate in exit:
        print(f"EXIT from {coordinate}.")
        assign_piece_cost(board, data)
        temp_dict = {}
        for i in board.keys():
            temp_dict[i] = board[i].cost[0]

        print_board(temp_dict)
    else:
        next_coordinate = total(board, coordinate, neighbours, exit)
        if next_coordinate[0] == coordinate[0] + 2 or next_coordinate[1] == coordinate[1] + 2:
            print(f"JUMP from {coordinate} to {next_coordinate}.")
        else:
            print(f"MOVE from {coordinate} to {next_coordinate}.")
        coordinate = next_coordinate
        data['pieces'].append(list(coordinate))
        assign_piece_cost(board, data)
        temp_dict = {}
        for i in board.keys():
            temp_dict[i] = board[i].cost[0]

        print_board(temp_dict)
    return

def total(board, coordinate, neighbours, exit):
    neighbours2 = []
    for i in neighbours:
        if sum(board[i].cost) <= sum(board[coordinate].cost):
            neighbours2.append((board[i].cost, i))
    return min(neighbours2)[1]

def dist_to_exit(board, piece, exit):
    dist = 0
    for i in exit:
        dist += (board[i].coordinates[0] - board[piece].coordinates[0])**2 + \
            (board[i].coordinates[1] - board[piece].coordinates[1])**2
    return dist

def multi_search(board, data, exit):
    colour = data['colour']
    while data['pieces']:
        piece_list = []
        ex = False
        for piece in data['pieces']:
            coordinate = tuple(piece)
            if coordinate in exit:
                ex = True
                break
            piece_list.append((board[coordinate].cost, tuple(piece)))
        if not ex:
            piece_list = sorted(piece_list)
            coordinate = piece_list[-1][1]
        single_move(board, coordinate, data, exit)

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
