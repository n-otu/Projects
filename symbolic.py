"""
6.101 Lab 11:
Symbolic Algebra
"""

import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    """Class to represent different types of symbols that are involved in algebra."""

    # default for precedence is zero
    precedence = 0

    # basic stuff for the symbols
    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __mul__(self, other):
        return Mul(self, other)

    def __truediv__(self, other):
        return Div(self, other)

    def __pow__(self, other):
        return Pow(self, other)

    # now the r_operation stuff for when stuff is switched
    def __radd__(self, other):
        if isinstance(other, str):
            return Add(Var(other), self)
        else:
            return Add(Num(other), self)

    def __rsub__(self, other):
        if isinstance(other, str):
            return Sub(Var(other), self)
        else:
            return Sub(Num(other), self)

    def __rmul__(self, other):
        if isinstance(other, str):
            return Mul(Var(other), self)
        else:
            return Mul(Num(other), self)

    def __rtruediv__(self, other):
        if isinstance(other, str):
            return Div(Var(other), self)
        else:
            return Div(Num(other), self)

    def __rpow__(self, other):
        if isinstance(other, str):
            return Pow(Var(other), self)
        else:
            return Pow(Num(other), self)

    def simplify(self):
        """numbers and variables simplify to themselves"""
        return self

    def __eq__(self, other):
        """dunder method to check if two expressions are equal"""

        # make sure they're the same type, both Num or Var
        if type(self) != type(other):
            return False

        # if Vars, check value inside
        if isinstance(self, Var):
            if self.name == other.name:
                return True
            return False

        # for Nums, same methodology
        if isinstance(self, Num):
            # both integers or floats
            if (isinstance(self.n, int) and isinstance(other.n, int)) or (
                isinstance(self.n, float) and isinstance(other.n, float)
            ):
                return self.n == other.n
            # set both to int so they still register as equal
            return int(self.n) == int(other.n)

class BinOp(Symbol):
    """Class that rerpresents binary operations."""

    # boolean for whether to wrap in special cases
    wrap_right_at_same_precedence = False

    def __init__(self, left, right):
        """
        Initializer.  Store an instance variables called `left` and 'right', 
        containing the
        value passed in to the initializer.
        """

        # Check if left is a symbol, if not, make it
        if isinstance(left, Symbol):
            self.left = left
        else:
            if isinstance(left, str):
                self.left = Var(left)
            else:
                self.left = Num(left)

        # same as left
        if isinstance(right, Symbol):
            self.right = right
        else:
            if isinstance(right, str):
                self.right = Var(right)
            else:
                self.right = Num(right)

    def eval(self, mapping):
        if self.operation == "-":
            return self.left.eval(mapping) - self.right.eval(mapping)
        if self.operation == "+":
            return self.left.eval(mapping) + self.right.eval(mapping)
        if self.operation == "*":
            return self.left.eval(mapping) * self.right.eval(mapping)
        if self.operation == "/":
            return self.left.eval(mapping) / self.right.eval(mapping)

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + repr(self.left)
            + ","
            + " "
            + repr(self.right)
            + ")"
        )

    def __eq__(self, other):
        left, right = self.left, self.right
        lefty, righty = other.left, other.right
        if self.operation == other.operation and (left == lefty) and (right == righty):
            return True
        return False

    def __str__(self):
        # addition and subtraction
        if self.operation in "+-":
            # for subtraction only
            if self.right.precedence == 1 and self.operation == "-":
                return (
                    str(self.left)
                    + " "
                    + self.operation
                    + " "
                    + "("
                    + str(self.right)
                    + ")"
                )
            return str(self.left) + " " + self.operation + " " + str(self.right)

        if self.operation == "*":
            # if multiplying two sums or differences
            if self.left.precedence == 1 and self.right.precedence == 1:
                return (
                    "("
                    + str(self.left)
                    + ")"
                    + " "
                    + self.operation
                    + " "
                    + "("
                    + str(self.right)
                    + ")"
                )

            # if first term is of lesser precedence
            if self.left.precedence == 1:
                return (
                    "("
                    + str(self.left)
                    + ")"
                    + " "
                    + self.operation
                    + " "
                    + str(self.right)
                )

            # if latter term is
            if self.right.precedence == 1:
                return (
                    str(self.left)
                    + " "
                    + self.operation
                    + " "
                    + "("
                    + str(self.right)
                    + ")"
                )

            # normal version of just two symbols
            return str(self.left) + " " + self.operation + " " + str(self.right)

        if self.operation == "/":
            # if dealing with sums or differences inside
            if self.left.precedence == 1 and self.right.precedence == 1:
                return (
                    "("
                    + str(self.left)
                    + ")"
                    + " "
                    + self.operation
                    + " "
                    + "("
                    + str(self.right)
                    + ")"
                )

            # if right is any operation (dealing with parenthesis)
            if self.right.precedence in (1,100):
                # and if left is any operation of lower precedence
                if self.left.precedence == 1:
                    return (
                        "("
                        + str(self.left)
                        + ")"
                        + " "
                        + self.operation
                        + " "
                        + "("
                        + str(self.right)
                        + ")"
                    )

                # then return result
                return (
                    str(self.left)
                    + " "
                    + self.operation
                    + " "
                    + "("
                    + str(self.right)
                    + ")"
                )

            # if earlier piece is of lower precedence
            if self.left.precedence == 1:
                return (
                    "("
                    + str(self.left)
                    + ")"
                    + " "
                    + self.operation
                    + " "
                    + str(self.right)
                )

            # normal case of division, no other operations to worry about
            return str(self.left) + " " + self.operation + " " + str(self.right)

    def simplify(self):
        # need to go through the entire expression
        left = self.left.simplify()
        right = self.right.simplify()

        if self.operation == "+":
            # two numbers, covers adding 0 and combining numbers
            if isinstance(left, Num) and isinstance(right, Num):
                return Num(left.n + right.n)

            # gets rid of extraneous zeros
            if isinstance(left, Num) and left.n == 0:
                return right
            if isinstance(right, Num) and right.n == 0:
                return left

            # if already ok in base form
            return left + right

        if self.operation == "-":
            # covers combining numbers
            if isinstance(left, Num) and isinstance(right, Num):
                return Num(left.n - right.n)

            # extraneous zeros
            if isinstance(right, Num) and right.n == 0:
                return left

            # already ok
            return left - right

        if self.operation == "*":
            # combine numbers
            if isinstance(left, Num) and isinstance(right, Num):
                return Num(left.n * right.n)

            # when multiplying by zero
            if (isinstance(left, Num) and left.n == 0) or (
                isinstance(right, Num) and right.n == 0
            ):
                return Num(0)
            # or by one
            if isinstance(left, Num) and left.n == 1:
                return right
            if isinstance(right, Num) and right.n == 1:
                return left

            # already ok
            return left * right

        if self.operation == "/":
            # dividing by zero
            if isinstance(left, Num) and left.n == 0:
                return Num(0)

            # or by one
            if isinstance(right, Num) and right.n == 1:
                return left

            # combining numbers
            if isinstance(left, Num) and isinstance(right, Num):
                return Num(left.n / right.n)

            # already ok
            return left / right


class Add(BinOp):
    """Operation of adding two symbols together."""

    # precedence same as sub, lower than mul and div
    precedence = 1
    operation = "+"

    def deriv(self, inp):
        return self.left.deriv(inp) + self.right.deriv(inp)


class Sub(BinOp):
    """Operation of subtracting a right symbol from a left one."""

    # precedence same as addition, lower than mul and div
    precedence = 1
    operation = "-"

    def deriv(self, inp):
        return self.left.deriv(inp) - self.right.deriv(inp)


class Mul(BinOp):
    """Class to represent binary operation of multiplying two symbols."""

    # same as div, higher than add and sub
    precedence = 100
    operation = "*"
    def deriv(self, inp):
        # use the product rule
        return self.left * self.right.deriv(inp) + self.right * self.left.deriv(inp)


class Div(BinOp):
    # same as mul, higher than add and sub
    precedence = 100
    operation = "/"

    def deriv(self, inp):
        return (
            self.right * self.left.deriv(inp) - self.left * self.right.deriv(inp)
        ) / (self.right * self.right)


class Pow(BinOp):
    """Class for exponents"""
    # higher than +-*/
    precedence = 1000
    operation = "**"
    wrap_left_at_same_precedence = False

    def __str__(self):
        # if dealing with sums or differences inside
        if self.left.precedence == 1 and self.right.precedence == 1:
            return (
                "("
                + str(self.left)
                + ")"
                + " "
                + self.operation
                + " "
                + "("
                + str(self.right)
                + ")"
            )

        # if right is any operation (dealing with parenthesis)
        if self.right.precedence in (1,100):
            # and if left is any operation of lower precedence
            if self.left.precedence == 1:
                return (
                    "("
                    + str(self.left)
                    + ")"
                    + " "
                    + self.operation
                    + " "
                    + "("
                    + str(self.right)
                    + ")"
                )

            # then return result
            return (
                str(self.left)
                + " "
                + self.operation
                + " "
                + "("
                + str(self.right)
                + ")"
            )

        # if earlier piece is of lower precedence
        if self.left.precedence in (1, 100):
            return (
                "("
                + str(self.left)
                + ")"
                + " "
                + self.operation
                + " "
                + str(self.right)
            )

        # normal case of division, no other operations to worry about
        return str(self.left) + " " + self.operation + " " + str(self.right)


class Var(Symbol):
    """Class that represents variables like x or y."""

    # lowest precedence
    operation = None
    precedence = 0

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"

    def eval(self, mapping):
        # make sure it's there
        if self.name in mapping.keys():
            return mapping[self.name]
        else:
            raise NameError

    def deriv(self, inp):
        """
        derivatives of variables
        """
        # derivative of a variable with respect to itself is one
        if inp == self.name:
            return Num(1)
        # otherwise, it is treated like a constant
        return Num(0)


class Num(Symbol):
    """Class that represents numbers"""

    # lowest precedence
    operation = None
    precedence = 0

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

    def eval(self, mapping):
        return self.n

    def deriv(self, inp):
        """
        derivative of a number is always zero
        """
        return Num(0)


numbers = "0123456789"
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
extra = "()+-*/"


def tokenize(text):
    """will take a string as described above as input and should output
    a list of meaningful tokens (parentheses, variable names, numbers, or
    operands)."""

    tokens = []

    # for when multiple things need to be grouped together, like -200.5
    word = ""

    # need indexes
    for numb, let in enumerate(text):
        # negative numbers, start building
        if let == "-" and text[numb + 1] != " ":
            word += let
        # for operands and parenthesis
        elif let in extra:
            if len(word) > 0:
                tokens.append(word)
                word = ""
            tokens.append(let)
        # everything else but spaces
        elif let != " ":
            word += let
    # add words if not empty
    if len(word) > 0:
        tokens.append(word)

    return tokens


def parse(tokens):
    """will take the output of tokenize and convert it into an
    appropriate instance of Symbol (or some subclass thereof)."""

    def parse_expression(index):
        """Will recursively take as an argument an integer indexing
        into the tokens list and return a pair of values."""

        # for every index
        token = tokens[index]

        if token in letters:
            return Var(token), index + 1

        # if opening parens and starting phrase
        elif token == "(":
            # go through both sides
            first, left = parse_expression(index + 1)
            last, right = parse_expression(left + 1)
            operation = tokens[left]

            # for every operation
            if operation == "+":
                return Add(first, last), right + 1
            elif operation == "-":
                return Sub(first, last), right + 1
            elif operation == "*":
                return Mul(first, last), right + 1
            elif operation == "/":
                return Div(first, last), right + 1

        # just numbers
        number = int(token)
        return Num(number), index + 1

    parsed, next_index = parse_expression(0)

    return parsed


def expression(res):
    """Just uses the functions above to parse strings into symbol objects"""
    return parse(tokenize(res))


if __name__ == "__main__":
    doctest.testmod()
