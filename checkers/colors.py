from enum import Flag, StrEnum


class ColorID(Flag):
    """Acts as an identifier for player pieces and tile squares.
    Can somewhat be treated as an integer (such as truthiness)."""

    DARK = 0
    LIGHT = 1


class Color(StrEnum):
    """Contains hex values of colors."""

    # App theme colors
    BG_APP = "#0f172a"
    BG_TOPBAR = "#111827"
    BG_CARD = "#1e293b"
    BG_PANEL = "#233247"
    BG_BUTTON = "#334155"
    BG_BUTTON_HOVER = "#475569"
    BG_DANGER = "#f43f5e"
    BG_DANGER_HOVER = "#e11d48"
    FG_TEXT = "#f8fafc"
    FG_MUTED = "#94a3b8"
    FG_ACCENT = "#f43f5e"

    # Highlight colors
    HL_SELECTED = "#3b82f6"
    HL_MOVES = "#60a5fa"
    HL_FORCED = "#f59e0b"
