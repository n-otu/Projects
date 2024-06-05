"""
6.101 Lab 13:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import sys

sys.setrecursionlimit(20_000)


#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    # split string on lines first
    lines = source.splitlines()
    new_str = ""
    parens = ("(", ")")

    for line in lines:
        for char in line:
            # stop looking at lines on ;
            if char == ";":
                break
            # split words and parens on spaces
            if char in parens:
                new_str += " "
                new_str += char
                new_str += " "

            else:
                new_str += char
        new_str += " "

    # now just make list of words and parens
    return new_str.split()


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    # make sure that the number of parenthesis match
    num_left = tokens.count("(")
    num_right = tokens.count(")")
    if num_left != num_right:
        raise SchemeSyntaxError

    # for lists with only one item that is not a parenthesis
    if len(tokens) == 1:
        if number_or_symbol(tokens[0]) != "(" or number_or_symbol(tokens[0]) != ")":
            return number_or_symbol(tokens[0])
        else:
            raise SchemeSyntaxError
    else:
        if tokens[0] != "(" or tokens[len(tokens) - 1] != ")":
            raise SchemeSyntaxError

    def list_constructor(index):
        """Construct lists from parens using resursion"""

        # make a new list on every open parenthesis
        if tokens[index] == "(":
            new_list = []
            next_index = index + 1
            # go on until the close parenthesis
            while tokens[next_index] != ")":
                # recursively go over every element
                newest_list, next_index = list_constructor(next_index)
                new_list.append(newest_list)
                try:
                    tokens[next_index]
                # make sure to deal with index errors
                except IndexError as fault:
                    raise SchemeSyntaxError from fault
            return new_list, next_index + 1

        # for normal items, just add them to the list
        else:
            num_syms = number_or_symbol(tokens[index])
            return num_syms, index + 1

    result, num = list_constructor(0)
    return result


######################
# Built-in Functions #
######################


def product(exp):
    """For multiplying numbers"""

    prod = 1
    for num in exp:
        prod = prod * num
    return prod


def divide(exp):
    """For dividing numbers"""

    if exp is None:
        raise SchemeEvaluationError

    if len(exp) == 1:
        return 1 / exp[0]

    start = exp[0]
    for num in exp[1:]:
        start /= num

    return start


def equal(exp):
    start = exp[0]
    for elem in exp:
        if elem != start:
            return False
    return True


def greater(exp):
    for num in range(len(exp) - 1):
        if exp[num] <= exp[num + 1]:
            return False
    return True


def lesser(exp):
    for num in range(len(exp) - 1):
        if exp[num] >= exp[num + 1]:
            return False
    return True


def nondec(exp):
    for num in range(len(exp) - 1):
        if exp[num] > exp[num + 1]:
            return False
    return True


def non_inc(exp):
    for num in range(len(exp) - 1):
        if exp[num] < exp[num + 1]:
            return False
    return True


def eq(exp):
    start = exp[0]
    for arg in exp[1:]:
        if arg != start:
            return False
    return True


def not_(arg):
    # should only have one argument
    if len(arg) != 1:
        raise SchemeEvaluationError

    if arg[0] is False:
        return True
    return False


def carf(cell):
    """get the car of a cons cell"""
    if len(cell) != 1 or not isinstance(cell[0], Pair):
        raise SchemeEvaluationError

    return cell[0].car


def cdrf(cell):
    """get the cdr of a cons cell"""
    if len(cell) != 1 or not isinstance(cell[0], Pair):
        raise SchemeEvaluationError

    return cell[0].cdr


def length(cell):
    if not list_check(cell):
        raise SchemeEvaluationError

    pair = cell[0]
    # once you hit the end
    if pair == []:
        return 0

    count = 1
    if cdrf([pair]) == []:
        return count
    else:
        count = count + length([cdrf([pair])])

    return count


def lis(inp):
    """get item at index in linked list"""
    
    pair = inp[0]
    ind = inp[1]
    
    # if list is a cons cell and not a list
    if isinstance(pair, Pair) and not list_check([pair]):
        if ind == 0:
            return carf([pair])
        else:  
            raise SchemeEvaluationError
    

    if 0 == ind:
        return carf([pair])
    
    return lis([cdrf([pair]), ind-1])

    

def concat(lists):
    """concatenate lists"""
    # # return a shallow copy if only one
    # if len(lists) == 1:
    #     return lists[0]

    # # called with no argument
    # if lists is None:
    #     return []

    # # flat = []
    # new = []

    # for pair in lists:
    #     if not isinstance(pair, Pair):
    #         raise SchemeEvaluationError
    #     # construct a new list

    #     # flat.append(pair)
    #     new.extend(pair)
    # return new
    if len(lists) == 1:
        return lists[0]

    # called with no argument
    if lists is None:
        return []

    flat = []

    for pair in lists:
        if not isinstance(pair, Pair):
            raise SchemeEvaluationError
        # construct a new list

        flat.append(carf([pair]))
        if list_check([cdrf([pair])]):
            flat.extend(concat(cdrf([pair])))
                      
        
    new = make_linked(flat)
    return const(new)


def const(inp):
    """turn "flat" list intk pair object"""
    if len(inp) != 2:
        raise SchemeEvaluationError

    return Pair(inp[0], inp[1])


def make_linked(inp=None):
    """function to turn a list into a linked list"""
    if inp == []:
        return []

    if len(inp) == 1:
        return Pair(inp[0], [])

    result = Pair(inp[0], make_linked(inp[1:]))
    return result


def mapping(inp):
    """takes a function and a list as arguments,
    and it returns a new list containing the results of
    applying the given function to each element of the given list."""
    func = inp[0]
    lis = inp[1]
    result = []
    for elem in lis:
        result.append(func(elem))
    return result


def filt(inp):
    """takes a function and a list as arguments,
    and it returns a new list containing only the
    elements of the given list for which the given
    function returns true."""

    func = inp[0]
    lis = inp[1]
    result = []

    if func(carf([lis])) is True:
        result.append(carf([lis]))
        return filt([func, cdrf([lis])])

    return result
    


def reduc(func, lis, init):
    """t produces its output by successively applying the
    given function to the elements in the list, maintaining
    an intermediate result along the way."""

    pass


def list_check(inp):
    """check if a given input is a linked list"""
    pair = inp[0]
    
    if pair == []:
        return True
    
    if isinstance(pair, Pair):   
        return list_check([cdrf([pair])]) 
    
    return False


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": product,
    "/": divide,
    "equal?": eq,
    ">": greater,
    "<": lesser,
    "<=": nondec,
    ">=": non_inc,
    "#t": True,
    "#f": False,
    "not": not_,
    "car": carf,
    "cdr": cdrf,
    "cons": const,
    "list": make_linked,
    "list?": list_check,
    "length": length,
    "nil": [],
    "list-ref": lis,
    "append": concat,
    "map": mapping,
    "filter": filt,
    "reduce": reduc,
}


##############
# Evaluation #
##############


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
        frame is where stuff is evaluated in. default is empty with parent of scheme
    """
    # print(tree, 'tree input')

    if frame is None:
        frame = Frames(parent=built_ins)

    # if expression is just a number
    if isinstance(tree, (int, float)):
        return tree

    # for already defined functions
    if isinstance(tree, str):
        if tree not in frame:
            raise SchemeNameError

        return frame[tree]

    # assuming tree is a list from this point

    if tree == []:
        raise SchemeEvaluationError

    first = tree[0]

    # when defining something
    if first == "define":
        # get variable name and value
        var, val = tree[1], tree[2]

        # shorter syntax implementation
        if isinstance(var, list):
            # turn it into new form
            same = ["define", var[0], ["lambda", var[1:], val]]

            return evaluate(same, frame)

        frame[var] = evaluate(val, frame)
        # return value after defining it
        return frame[var]

    # special form for "and"
    elif first == "and":
        for arg in tree[1:]:
            if evaluate(arg, frame) is False:
                return False
        return True

    # specal form for "or"
    elif first == "or":
        for arg in tree[1:]:
            if evaluate(arg, frame) is True:
                return True
        return False

    # special form for "if"
    elif first == "if":
        pred = tree[1]
        # print(pred, evaluate(pred, frame), 'pred and evaluation')
        true_exp = tree[2]
        false_exp = tree[3]

        if evaluate(pred, frame) is True:
            return evaluate(true_exp, frame)
        else:
            return evaluate(false_exp, frame)

    # defining a function
    elif first == "lambda":
        new_func = Function(tree[1], tree[2], frame)
        return new_func

    res = evaluate(first, frame)

    if not callable(res):
        raise SchemeEvaluationError

    others = [evaluate(value, frame) for value in tree[1:]]

    return res(others)


class Frames(object):
    """Class to represent frames"""

    def __init__(self, parent=None):
        # every frame can have a parent and values
        self.parent = parent
        # variable names as keys and values as values
        self.variables = dict()

    def __setitem__(self, variable, value):
        self.variables[variable] = value

    def __contains__(self, variable):
        if variable in self.variables:
            return True

        # check parent frame if not inside this one
        if self.parent is not None:
            return self.parent.__contains__(variable)

        return False

    def __getitem__(self, variable):
        if variable in self.variables:
            return self.variables[variable]

        if self.parent is None:
            raise SchemeNameError

        return self.parent.__getitem__(variable)

    def __str__(self):
        return "variables: " + str(self.variables) + "\n" + "parent:" + str(self.parent)


built_ins = Frames()
built_ins.variables = scheme_builtins


class Function(object):
    """Class to represent user-defined functions
    has parameters, function body, and frame"""

    def __init__(self, params, func, frame):
        self.params = params
        self.func = func
        self.frame = frame

    def __call__(self, args):
        if len(self.params) != len(args):
            raise SchemeEvaluationError

        new = Frames(parent=self.frame)
        # bind arguments to parameters in new frame
        for num in range(len(args)):
            new.variables[self.params[num]] = args[num]

        return evaluate(self.func, new)

    def __str__(self):
        """
        string representation of function stored in object
        """
        return "function to do: " + str(self.func)


class Pair(object):
    """class to represent a cons cell"""

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __call__(self, args):
        new = Frames(parent=self.frame)
        for num in range(len(args)):
            new.variables[self.params[num]] = args[num]

        # check that exactly 2 arguments
        if len(args) != 2:
            raise SchemeEvaluationError

        # print('passing in', args[0], args[1])
        return Pair(args[0], [args[1]])

    def __repr__(self):
        return "Pair(" + str(self.car) + ", " + str(self.cdr)


def result_and_frame(tree, frame=None):
    """returns a tuple with two elements: the result of the
    evaluation and the frame in which the expression was evaluated"""

    # if no frame was given, default is scheme builtin stuff
    if frame is None:
        frame = Frames(parent=built_ins)

    return (evaluate(tree, frame), frame)


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    schemerepl.SchemeREPL(use_frames=True, verbose=False).cmdloop()
    
