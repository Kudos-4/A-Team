import tkinter as tk
from pathlib import Path
from typing import Optional

from PIL import Image, ImageTk

from checkers.game import Game, King
from checkers.types import Position

_ASSET_DIR = Path("checkers") / "user_interface" / "assets"
_BOARD_SIZE = (8, 8)
_TILE_PX = 72

_ICON_FILES = {
    "light-tile": "LightTile.png",
    "dark-tile": "DarkTile.png",
    "dark-pawn": "DarkPawn.png",
    "dark-king": "DarkKing.png",
    "light-pawn": "LightPawn.png",
    "light-king": "LightKing.png",
}


def _notation_to_pos(notation: int) -> Position:
    """Convert 1-32 checkers square notation to (row, col) board position."""
    row = (notation - 1) // 4
    idx = (notation - 1) % 4
    col = idx * 2 + 1 if row % 2 == 0 else idx * 2
    return (row, col)


def _parse_move(move_str: str) -> Optional[Position]:
    """Parse '12-16' or '12x22' into (from_notation, to_notation)."""
    try:
        sep = "x" if "x" in move_str else "-"
        a, b = move_str.split(sep)
        return int(a), int(b)
    except (ValueError, IndexError):
        return None


def _snapshot(game: Game) -> dict[Position, tuple[str, str]]:
    """Return {position: (color, piece_type)} for all current pieces."""
    state: dict[Position, tuple[str, str]] = {}
    for piece in game.dark_pieces:
        state[piece.position] = ("dark", "king" if isinstance(piece, King) else "pawn")
    for piece in game.light_pieces:
        state[piece.position] = ("light", "king" if isinstance(piece, King) else "pawn")
    return state


def _build_snapshots(
    moves: list[str],
) -> list[dict[Position, tuple[str, str]]]:
    """Simulate each move and collect a board snapshot after each one."""
    game = Game(_BOARD_SIZE)
    snapshots = [_snapshot(game)]
    for move_str in moves:
        parsed = _parse_move(move_str)
        if parsed is None:
            break
        src = _notation_to_pos(parsed[0])
        dst = _notation_to_pos(parsed[1])
        try:
            game.move_piece(src, dst)
        except Exception:
            break
        snapshots.append(_snapshot(game))
    return snapshots


class ReplayScreen(tk.Toplevel):
    """Step-through board replay for a completed checkers game."""

    _BG = "#0f172a"
    _BG_CARD = "#1e293b"
    _BG_PANEL = "#233247"
    _BG_BTN = "#334155"
    _BG_BTN_HV = "#475569"
    _FG = "#f8fafc"
    _FG_MUTED = "#94a3b8"
    _ACCENT = "#f43f5e"
    _TILE_DARK = "#1f2937"
    _TILE_LIGHT = "#334155"
    _HL_MOVE = "#f59e0b"

    def __init__(
        self,
        parent: tk.Widget,
        moves: list[str],
        opponent: str,
        result: str,
        date: str,
    ) -> None:
        super().__init__(parent)
        self.title(f"Replay — vs {opponent}")
        self.configure(bg=self._BG)
        self.resizable(False, False)

        self._moves = moves
        self._snapshots = _build_snapshots(moves)
        self._step = 0
        self._icons = self._load_icons()
        self._tile_btns: list[list[tk.Button]] = []
        self._tile_bg: dict[Position, str] = {}

        self._build_ui(opponent, result, date)
        self._render(0)
        self._center()

    def _load_icons(self) -> dict[str, ImageTk.PhotoImage]:
        icons: dict[str, ImageTk.PhotoImage] = {}
        for key, filename in _ICON_FILES.items():
            icons[key] = ImageTk.PhotoImage(
                Image.open(_ASSET_DIR / filename).resize((_TILE_PX, _TILE_PX))
            )
        return icons

    def _build_ui(self, opponent: str, result: str, date: str) -> None:
        header = tk.Frame(self, bg=self._BG)
        header.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(
            header,
            text="REPLAY",
            font=("Arial", 20, "bold"),
            fg=self._ACCENT,
            bg=self._BG,
        ).pack(side="left")
        tk.Label(
            header,
            text=f"vs {opponent}  |  {result}  |  {date}",
            font=("Arial", 11),
            fg=self._FG_MUTED,
            bg=self._BG,
        ).pack(side="left", padx=14)

        body = tk.Frame(self, bg=self._BG)
        body.pack(fill="both", expand=True, padx=16, pady=8)

        self._init_board(body)

        panel = tk.Frame(body, bg=self._BG_CARD, padx=10, pady=10)
        panel.pack(side="left", fill="y", padx=(14, 0))
        tk.Label(
            panel,
            text="Move List",
            font=("Arial", 11, "bold"),
            fg=self._FG_MUTED,
            bg=self._BG_CARD,
        ).pack(anchor="w", pady=(0, 4))

        self._move_list = tk.Text(
            panel,
            width=18,
            height=24,
            bg=self._BG_PANEL,
            fg=self._FG,
            font=("Consolas", 10),
            bd=0,
            relief="flat",
            padx=6,
            pady=6,
            state="disabled",
        )
        self._move_list.pack()
        self._move_list.tag_configure(
            "current", background=self._HL_MOVE, foreground="#000000"
        )
        self._populate_move_list()

        nav = tk.Frame(self, bg=self._BG)
        nav.pack(pady=(4, 14))

        self._prev_btn = tk.Button(
            nav,
            text="← Prev",
            font=("Arial", 11, "bold"),
            bg=self._BG_BTN,
            fg=self._FG,
            activebackground=self._BG_BTN_HV,
            activeforeground=self._FG,
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._step_back,
        )
        self._prev_btn.pack(side="left", padx=6)

        self._step_lbl = tk.Label(
            nav, text="", font=("Arial", 11), fg=self._FG, bg=self._BG, width=14
        )
        self._step_lbl.pack(side="left", padx=8)

        self._next_btn = tk.Button(
            nav,
            text="Next →",
            font=("Arial", 11, "bold"),
            bg=self._BG_BTN,
            fg=self._FG,
            activebackground=self._BG_BTN_HV,
            activeforeground=self._FG,
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._step_forward,
        )
        self._next_btn.pack(side="left", padx=6)

        self.bind("<Left>", lambda _e: self._step_back())
        self.bind("<Right>", lambda _e: self._step_forward())

    def _init_board(self, parent: tk.Widget) -> None:
        board_frame = tk.Frame(parent, bg=self._BG)
        board_frame.pack(side="left")
        rows, cols = _BOARD_SIZE
        for i in range(rows):
            row_btns: list[tk.Button] = []
            for j in range(cols):
                pos = (i, j)
                is_dark = (i + j) % 2 == 1
                bg = self._TILE_DARK if is_dark else self._TILE_LIGHT
                self._tile_bg[pos] = bg
                btn = tk.Button(
                    board_frame,
                    image=self._icons["dark-tile" if is_dark else "light-tile"],
                    bg=bg,
                    activebackground=bg,
                    bd=0,
                    relief="flat",
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                row_btns.append(btn)
            self._tile_btns.append(row_btns)

    def _populate_move_list(self) -> None:
        self._move_list.configure(state="normal")
        self._move_list.delete("1.0", "end")
        for i, move in enumerate(self._moves):
            self._move_list.insert("end", f"{i + 1:>3}. {move}\n")
        self._move_list.configure(state="disabled")

    def _render(self, step: int) -> None:
        self._step = step
        snapshot = self._snapshots[step]
        rows, cols = _BOARD_SIZE

        for i in range(rows):
            for j in range(cols):
                pos = (i, j)
                if pos in snapshot:
                    color, ptype = snapshot[pos]
                    image_key = f"{color}-{ptype}"
                else:
                    is_dark = (i + j) % 2 == 1
                    image_key = "dark-tile" if is_dark else "light-tile"
                self._tile_btns[i][j].configure(image=self._icons[image_key])

        total = len(self._moves)
        self._step_lbl.configure(text=f"Move {step} of {total}")
        self._prev_btn.configure(state="normal" if step > 0 else "disabled")
        self._next_btn.configure(
            state="normal" if step < len(self._snapshots) - 1 else "disabled"
        )

        self._move_list.configure(state="normal")
        self._move_list.tag_remove("current", "1.0", "end")
        if step > 0:
            self._move_list.tag_add("current", f"{step}.0", f"{step}.end+1c")
            self._move_list.see(f"{step}.0")
        self._move_list.configure(state="disabled")

    def _step_back(self) -> None:
        if self._step > 0:
            self._render(self._step - 1)

    def _step_forward(self) -> None:
        if self._step < len(self._snapshots) - 1:
            self._render(self._step + 1)

    def _center(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")
