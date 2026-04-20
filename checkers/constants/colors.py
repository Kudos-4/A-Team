from enum import Flag, StrEnum


class ColorID(Flag):
    """Acts as an identifier for player pieces and tile squares.
    Can somewhat be treated as an integer (such as truthiness)."""

    DARK = 0
    LIGHT = 1


class Color(StrEnum):
    """Contains hex values of colors."""

    CHARCOAL = "#26242f"
