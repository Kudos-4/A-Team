from enum import Flag, StrEnum


class ColorID(Flag):
    """Acts as an identifier for player pieces and tile squares.
    Can be treated as a bit subclassed from integer.
    Can be negated (~) to flip flags or used for truthiness."""

    DARK = 0
    LIGHT = 1


class Color(StrEnum):
    """Contains hex values of colors."""

    # App theme colors
    BLACK = "#000000"
    BG_APP = "#0f172a"
    BG_TOPBAR = "#111827"
    BG_CARD = "#1e293b"
    BG_PANEL = "#233247"
    BG_BUTTON = "#334155"
    BG_BUTTON_DARK = "#1f2937"
    BG_BUTTON_HOVER = "#475569"
    BG_DANGER = "#f43f5e"
    BG_DANGER_HOVER = "#e11d48"
    FG_TEXT = "#f8fafc"
    FG_MUTED = "#94a3b8"
    FG_ACCENT = "#f43f5e"

    # AuthUI
    ERROR = "#ef4444"
    SUCCESS = "#22c55e"

    # GameHistoryScreen
    BG_ROW_A = "#243447"
    BG_ROW_B = "#1f2f42"
    MV_RECORD_BTN = "#2563eb"

    # Highlight colors
    HL_SELECTED = "#3b82f6"
    HL_MOVES = "#60a5fa"
    HL_FORCED = "#f59e0b"
