"""
COMP30024 Artificial Intelligence, Semester 1 2019
Solution to Project Part A: Searching

Authors:
"""

import sys
import json

def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)

    board = add_hexes(data)
    exit = exit_list(data, board)
    assign_cost(board, exit_list(data, board))

    temp_dict = {}
    for i in board.keys():
        temp_dict[i] = board[i].cost

    print_board(temp_dict)
    for piece in data['pieces']:
        search_one(board, piece, exit)

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

def add_hexes(data):
    board = {}
    for i in range(-3,1):
        for j in range(-3-i, 4):
            board[(i,j)] = Hex(1000, [], 'white', (i,j))
    for i in range(1,4):
        for j in range(-3,4-i):
            board[(i,j)] = Hex(1000, [], 'white', (i,j))

    for piece in data['pieces']:
        board[tuple(piece)].colour = data['colour']
    for block in data['blocks']:
        board[tuple(block)].colour = 'black'

    for k,v in board.items():
        for i in range(-1,2):
            for j in range(-1,2):
                new_coord = (k[0]+i,k[1]+j)
                if i != j and new_coord in board:
                    if board[new_coord].colour == 'white':
                        v.neighbours.append(board[new_coord])
                    elif (new_coord[0] + i, new_coord[1] + j) in board and board[(new_coord[0] + i, new_coord[1] + j)].colour == 'white':
                        v.neighbours.append(board[(new_coord[0] + i, new_coord[1] + j)])
    return board

def exit_list(data, board):
    lst = []
    print(data['colour'])
    if data['colour'] == 'red':
        for i in [(3,-3), (3,-2), (3,-1), (3,0)]:
            if board[i].colour != 'black':
                board[i].cost = 1
                lst.append(i)

    elif data['colour'] == 'blue':
        for i in [(0,-3), (-1,-2), (-2,-1), (-3,0)]:
            if board[i].colour != 'black':
                board[i].cost = 1
                lst.append(i)
    else:
        for i in [(-3,3), (-2,3), (-1,3), (0,3)]:
            if board[i].colour != 'black':
                board[i].cost = 1
                lst.append(i)
    return lst

def assign_cost(board, queue):
    while queue != []:
        curr = board[queue.pop(0)]
        for i in curr.neighbours:
            if i.cost > (curr.cost + 1):
                i.cost = curr.cost + 1
                queue.append(i.coordinates)

def single_move(board, piece, exit):
    return


def search_one(board, piece, exit):
    coordinate = tuple(piece)
    colour = board[coordinate].colour
    while coordinate not in exit:
        neighbours2 = sorted([(n.cost, n.coordinates) for n in board[coordinate].neighbours])
        mincost = neighbours2[0][0]
        neighbours3 = [neighbours2.pop(0)[1]]
        while neighbours2 and neighbours2[0][0] == mincost:
            neighbours3.append(neighbours2.pop(0)[1])

        # direction of travel -- along paths
        if coordinate[1] <= 0 and (coordinate[0] + 1, coordinate[1]) in neighbours3:
            next_coordinate = (coordinate[0] + 1, coordinate[1])
        elif coordinate[1] <= 0 and (coordinate[0] + 2, coordinate[1]) in neighbours3:
            next_coordinate = (coordinate[0] + 2, coordinate[1])
        elif (coordinate[0] + coordinate[1] >= 0) and (coordinate[0]+1, coordinate[1]+1) in neighbours3:
            next_coordinate = (coordinate[0]+1, coordinate[1]+1)
        elif (coordinate[0] + coordinate[1] >= 0) and (coordinate[0]+2, coordinate[1]+2) in neighbours3:
            next_coordinate = (coordinate[0]+1, coordinate[1]+1)
        else:
            next_coordinate = neighbours3[0]

        # printing moves
        if next_coordinate[0] == coordinate[0] + 2 or next_coordinate[1] == coordinate[1] + 2:
            print(f"JUMP from {coordinate} to {next_coordinate}.")
        else:
            print(f"MOVE from {coordinate} to {next_coordinate}.")
        coordinate = next_coordinate

    print(f"EXIT from {coordinate}.")


def search_two(board, pieces, exit):
    pieces_sorted = sorted([(n.cost, n.coordinates) for n in pieces])
    furthest = tuple(pieces_sorted[-1][1])
    second_furthest_cost = pieces_sorted[-2][0]
    while board[furthest].cost >= second_furthest_cost:
        pass


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
