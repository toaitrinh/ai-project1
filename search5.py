"""
COMP30024 Artificial Intelligence, Semester 1 2019
Solution to Project Part A: Searching

Authors:
"""

import sys
import json

"""
class for storing the board layout
"""
class Hex:
    def __init__(self, cost, neighbours, colour, coordinates):

        # cost from moving from specific hex
        # to exit, independently
        self.cost = cost

        # list of neighbouring hexes, stored as hex objects
        self.neighbours = neighbours

        # colour of hex, blocks stored as black
        # and empty hexes as white
        self.colour = colour

        # coordinates of hex
        self.coordinates = coordinates

def main():

    # import the board specifications
    with open(sys.argv[1]) as file:
        data = json.load(file)

    # convert data values for pieces and blocks from
    # list of lists to list of tuples
    list_to_tuple(data)

    # initialise the board
    board = {}
    exit = assign_piece_cost(board, data)

    # search for exit within board
    multi_search(board, data, exit)

"""
list_to_tuple changes the data values for pieces and blocks
from a list of lists, to list of tuples
"""
def list_to_tuple(data):
    data['pieces'] = [tuple(i) for i in data['pieces']]
    data['blocks'] = [tuple(i) for i in data['blocks']]

"""
assign_piece_cost takes the current board information from data
to determine the current board state
"""
def assign_piece_cost(board, data):

    # initialise the hexagonal game board
    add_hexes(board, data)

    # determine the goal hexes based on colour of pieces
    exit = exit_list(board, data)
    exit_copy = exit[:]

    # determine cost from exiting from piece location
    assign_cost(board, exit)
    return exit_copy

"""
add_hexes creates the board, intialising the cost, neighbours,
colour and coordinates of each individual hex
"""
def add_hexes(board, data):

    # add possible coordinates of hexes in game board_dict
    # initialise cost of each piece to 1000 and colour to white
    for i in range(-3,1):
        for j in range(-3-i, 4):
            board[(i,j)] = Hex([1000], [], 'white', (i,j))
    for i in range(1,4):
        for j in range(-3,4-i):
            board[(i,j)] = Hex([1000], [], 'white', (i,j))

    # change colour of pieces to colour in data
    for block in data['pieces']:
        board[block].colour = data['colour']

    # change colour of blocks to black
    for block in data['blocks']:
        board[tuple(block)].colour = 'black'

    # add all possible neighbours for a piece, dependant on piece colour
    for k,v in board.items():
        # possible neighbours have a difference within the below list
        for i,j in [(-1,0),(-1,1), (0,-1), (0,1), (1,0), (1,-1)]:
            new = (k[0]+i,k[1]+j)

            # white (empty) pieces are neighbours to any other hex that is
            # not a block
            if new in board and board[k].colour == 'white':
                if board[new].colour != 'black':
                    v.neighbours.append(board[new])
                elif (new[0] + i, new[1] + j) in board and (
                board[(new[0] + i, new[1] + j)].colour != 'black'):
                    v.neighbours.append(board[(new[0] + i, new[1] + j)])

            # coloured pieces cannot move or jump to a non-white hex
            elif new in board and board[k].colour != 'black':
                if board[new].colour == 'white':
                    v.neighbours.append(board[new])
                elif (new[0] + i, new[1] + j) in board and (
                board[(new[0] + i, new[1] + j)].colour == 'white'):
                    v.neighbours.append(board[(new[0] + i, new[1] + j)])

"""
exit_list initialises the cost of the exit pieces in board and returns
the possible exits dependent on the colour of the piece_list
"""
def exit_list(board, data):

    # initialise all non-black exit pieces with a cost of 1, representing
    # the number of moves to exit from an exit piece
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

"""
assign_cost determines the number of steps required to exit from a specific
coordinate in the board using breadth first search
"""
def assign_cost(board, queue):

    # we initialise the queue with the exit pieces
    while queue != []:

        # we evauluate the node at the start of the queue
        curr = board[queue.pop(0)]

        # if a neighbour of the current node has a cost higher than 1 more than
        # the current node's cost we change the neighbour's cost and add the
        # neighbour to the queue
        for i in curr.neighbours:
            if i.cost[0] > (curr.cost[0] + 1):
                i.cost[0] = curr.cost[0] + 1
                queue.append(i.coordinates)

"""
multi_search takes the initial board state and the current data, to formulate
a path for all pieces to exit the board starting from the closest piece
"""
def multi_search(board, data, exit):

    # find a path to exit for all the pieces on the board
    while data['pieces']:

        # move a piece that is closest to the exit
        path_list = [(board[i].cost, board[i].coordinates) for i in data['pieces']]
        single_move(board, min(path_list)[1], data, exit)

"""
single_move takes the current board state and the coordinates of piece and
finds a neighbour that takes the piece closer to the exit, whilst reforming
the board
"""
def single_move(board, piece, data, exit):

    # find the coordinates of all neighbours of the current piece
    neighbours = [n.coordinates for n in board[piece].neighbours]

    #remove the piece from the list of pieces and change the associated hex
    # to white
    data['pieces'].remove(piece)
    board[piece].colour = 'white'

    # if the piece is at an exit hex, we re-evauluate the board immediately
    if piece in exit:
        print(f"EXIT from {piece}.")
        assign_piece_cost(board, data)
        return

    # we find the neighbour that takes the piece closest to the exit this new
    # coordinate is added to the list of pieces and re-evaluate the board
    else:

        # find the hex that takes the piece closest to the exit
        next = total(board, neighbours, exit)
        if abs(next[0] - piece[0]) == 2 or abs(next[1] -piece[1]) == 2:
            print(f"JUMP from {piece} to {next}.")
        else:
            print(f"MOVE from {piece} to {next}.")
        data['pieces'].append(next)
        assign_piece_cost(board, data)
        return

"""
total takes the current board state and the neighbours of a pieces
and finds the neighbour that takes the piece closest to the exit
"""
def total(board, neighbours, exit):
    neighbours2 = []

    # add the neighbours to a new_list with its associated cost
    for i in neighbours:
        neighbours2.append((board[i].cost, i))

    # return a neighbour with the lowest cost
    return min(neighbours2)[1]

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
