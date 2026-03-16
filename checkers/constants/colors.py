from enum import Enum, Flag


class ColorID(Flag):
    """
    Acts as an identifier for player pieces and tile squares.
    Can somewhat be treated as an integer (such as truthiness).
    """

    BLACK = 0
    WHITE = 1


class Color(Enum):
    """Holds tuples containing RGB values."""

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
