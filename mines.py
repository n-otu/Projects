"""
6.101 Lab 7:
Six Double-Oh Mines
"""
#!/usr/bin/env python3

# import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys. If you modify this you will need
    # to update the docstrings in other functions!
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(nrows, ncolumns, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mines (list): List of mines, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((nrows, ncolumns), mines)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mines (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one mine
    is visible on the board after digging (i.e. game['visible'][mine_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    mine) and no mines are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    return dig_nd(game, (row, col))


def render_2d_locations(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored
    and all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, all_visible)


def render_2d_board(game, all_visible=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    list_board = render_2d_locations(game, all_visible)
    total_str = ""
    for lis in list_board:
        row_string = ""
        for char in lis:
            row_string += char
        total_str += row_string + "\n"

    return total_str[:-1]


# N-D IMPLEMENTATION


# helper functions


def get_neighbors(coordinates, dimensions):
    """A function that returns all the neighbors
    of a given set of coordinates in a given game as a list of tuples.
    The tuples will have a comma after the number if there is only one. A
    coordinate is a neighbor of itself."""

    def bounds(dimension, coordinate):
        return 0 <= coordinate < dimension

    poss_neighbors = [-1, 0, 1]
    neighbors = []
    # if the coordinate is one-dimensional
    if len(coordinates) == 1:
        # add every neighboring variation to the list
        for numb in coordinates:
            for step in poss_neighbors:
                if bounds(dimensions[0], numb + step):
                    neighbors.append((numb + step,))
        return neighbors

    first = []

    # first, start with the first number in the coordinate
    # for numb in coordinates:
    for step in poss_neighbors:
        if bounds(dimensions[0], coordinates[0] + step):
            first.append(coordinates[0] + step)

    # then do the same for every other number in the coordinate, storing all variations
    recurs = get_neighbors(coordinates[1:], dimensions[1:])
    for nei in first:
        for val in recurs:
            neighbors.append((nei,) + val)
    return neighbors


def get_values(array, dimensions, coordinate):
    """A function that, given an N-d array and a tuple coordinate,
    returns the value at that coordinates in the array.

    dimensions (tuple): Dimensions of the board
    coordinates (tuple): location
    """

    # want to gradually decrease number of dimensions

    # base case is one dimensional array
    if len(dimensions) == 1:
        return array[coordinate[0]]

    else:
        # minimize dimensions and coordinates

        new_array = array[coordinate[0]]

        return get_values(new_array, dimensions[1:], coordinate[1:])


def replace_val(array, dimensions, coordinates, value):
    """A function that, given an N-d array, a tuple of coordinates,
    and a value, replaces the value at those coordinates in the array with the given
    value. Will return None. Very similar to get_value. Coordinates is a tuple"""

    # want to gradually decrease number of dimensions

    # base case is one dimensional array
    if len(dimensions) == 1:
        array[coordinates[0]] = value
        return None

    else:
        # minimize dimensions and coordinates

        return replace_val(
            array[coordinates[0]], dimensions[1:], coordinates[1:], value
        )


def array_of_one(dimensions, value):
    """A function that, given a list of dimensions and a value,
    creates a new N-d array with those dimensions, where each value in
    the array is the given value."""

    if len(dimensions) == 1:
        new_array = []
        # you just want that value to repeat for however long the line itself is
        for num in range(dimensions[0]):
            new_array.append(value)
        return new_array

    else:
        array = []
        dimen = list(dimensions)

        dimen.pop(0)
        for lis in range(dimensions[0]):
            array.append(array_of_one(dimen, value))
    return array


def all_coordinates(dimensions):
    """A function that returns all possible coordinates in a given board.
    The return is a list of tuples"""

    coordinate_list = []

    if len(dimensions) == 1:
        for number in dimensions:
            for numb in range(number):
                coordinate_list.append((numb,))
        return coordinate_list

    first = []

    # first, start with the first number in the coordinate
    # for numb in coordinates:
    for num in range(dimensions[0]):
        first.append(num)

    # then do the same for every other number in the coordinate, storing all variations
    recurs = all_coordinates(dimensions[1:])
    for nei in first:
        for val in recurs:
            coordinate_list.append((nei,) + val)
    return coordinate_list


def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """

    # everything should be hidden at first
    visible = array_of_one(dimensions, False)

    # initialize a board with only zeros
    board = array_of_one(dimensions, 0)

    # first, add in the bombs
    for coord in mines:
        replace_val(board, dimensions, coord, ".")

    # now add in numbers indicating distance of bombs, starting with the ones

    neighboring = mines
    # first, identify the location of the numbers, then replace
    for coord in neighboring:
        number_coordinates = get_neighbors(coord, dimensions)
        for number in number_coordinates:
            if get_values(board, dimensions, number) != ".":
                replace_val(
                    board,
                    dimensions,
                    number,
                    int(get_values(board, dimensions, number)) + 1,
                )
        # then change out what you are neighboring
        neighboring = number_coordinates

    return {
        "dimensions": dimensions,
        "board": board,
        "visible": visible,
        "state": "ongoing",
    }


def victory_check(game):
    """Will check if the game has been won."""
    visible_safe = 0
    for coord in all_coordinates(game["dimensions"]):
        if (
            get_values(game["visible"], game["dimensions"], coord) == False
            and get_values(game["board"], game["dimensions"], coord) != "."
        ):
            visible_safe += 1

    if visible_safe == 0:
        game["state"] = "victory"


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """

    def dig_recurs(game, coordinates):
        """The actual digging function using recursion. Just separated."""

        if game["state"] == "defeat" or game["state"] == "victory":
            return 0

        # if it i already revealed
        if get_values(game["visible"], game["dimensions"], coordinates) == True:
            return 0

        # if a bomb
        if get_values(game["board"], game["dimensions"], coordinates) == ".":
            game["state"] = "defeat"
            replace_val(game["visible"], game["dimensions"], coordinates, True)

            return 1

        if get_values(game["board"], game["dimensions"], coordinates) > 0:
            replace_val(game["visible"], game["dimensions"], coordinates, True)
            return 1

        # update hidden, reveal spot
        replace_val(game["visible"], game["dimensions"], coordinates, True)

        # reveal neighbors too
        neighboring = get_neighbors(coordinates, game["dimensions"])

        # starting at 1 to count initial dig
        squares_revealed = 1
        # keep track of what squares are dug up

        # don't reveal neighbors if they are a bomb or bomb-adjacent
        for coord in neighboring:
            squares_revealed += dig_recurs(game, coord)
        return squares_revealed

    squares = dig_recurs(game, coordinates)
    victory_check(game)
    return squares


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    # initialize board of zeroes
    board = array_of_one(game["dimensions"], 0)
    # get all possible coordinates
    all_coordinate = all_coordinates(game["dimensions"])

    for coordinate in all_coordinate:
        # if it should be hidden
        if all_visible == False:
            # if a coordinate should be hidden, show that. Otherwise, leave it
            if get_values(game["visible"], game["dimensions"], coordinate) == False:
                replace_val(board, game["dimensions"], coordinate, "_")
            # first, replace the 0s with empty spaces
            elif get_values(game["board"], game["dimensions"], coordinate) == 0:
                # print(get_values(game['board'], game['dimensions'], coordinate))
                replace_val(board, game["dimensions"], coordinate, " ")

            else:
                val = get_values(game["board"], game["dimensions"], coordinate)
                replace_val(board, game["dimensions"], coordinate, str(val))
        else:
            # replace the 0s with empty spaces
            if get_values(game["board"], game["dimensions"], coordinate) == 0:
                # print(get_values(game['board'], game['dimensions'], coordinate))
                replace_val(board, game["dimensions"], coordinate, " ")
            else:
                val = get_values(game["board"], game["dimensions"], coordinate)
                replace_val(board, game["dimensions"], coordinate, str(val))
    return board


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    doctest.run_docstring_examples(
        render_2d_locations, globals(), optionflags=_doctest_flags, verbose=False
    )
