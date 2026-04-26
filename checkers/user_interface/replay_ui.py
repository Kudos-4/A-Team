from typing import Optional

import tkinter as tk

from checkers.user_interface import AssetHandler
from checkers.game import Game, King
from checkers.types import Position
from checkers.colors import ColorID, Color

BOARD_SIZE = (8, 8)


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
    game = Game(BOARD_SIZE)
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


    def __init__(
        self,
        parent: tk.Toplevel,
        moves: list[str],
        opponent: str,
        result: str,
        date: str,
    ) -> None:
        super().__init__(parent)
        self.title(f"Replay — vs {opponent}")
        self.configure(bg=Color.BG_APP)
        self.resizable(False, False)

        self._moves = moves
        self._snapshots = _build_snapshots(moves)
        self._step = 0
        self._icons = AssetHandler(icon_pixel_size=72)
        self._tile_btns: list[list[tk.Button]] = []
        self._tile_bg: dict[Position, str] = {}

        self._build_ui(opponent, result, date)
        self._render(0)
        self._center()

    def _build_ui(self, opponent: str, result: str, date: str) -> None:
        header = tk.Frame(self, bg=Color.BG_APP)
        header.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(
            header,
            text="REPLAY",
            font=("Arial", 20, "bold"),
            fg=Color.FG_ACCENT,
            bg=Color.BG_APP,
        ).pack(side="left")
        tk.Label(
            header,
            text=f"vs {opponent}  |  {result}  |  {date}",
            font=("Arial", 11),
            fg=Color.FG_MUTED,
            bg=Color.BG_APP,
        ).pack(side="left", padx=14)

        body = tk.Frame(self, bg=Color.BG_APP)
        body.pack(fill="both", expand=True, padx=16, pady=8)

        self._init_board(body)

        panel = tk.Frame(body, bg=Color.BG_CARD, padx=10, pady=10)
        panel.pack(side="left", fill="y", padx=(14, 0))
        tk.Label(
            panel,
            text="Move List",
            font=("Arial", 11, "bold"),
            fg=Color.FG_MUTED,
            bg=Color.BG_CARD,
        ).pack(anchor="w", pady=(0, 4))

        self._move_list = tk.Text(
            panel,
            width=18,
            height=24,
            bg=Color.BG_PANEL,
            fg=Color.FG_TEXT,
            font=("Consolas", 10),
            bd=0,
            relief="flat",
            padx=6,
            pady=6,
            state="disabled",
        )
        self._move_list.pack()
        self._move_list.tag_configure(
            "current", background=Color.HL_FORCED, foreground=Color.BLACK
        )
        self._populate_move_list()

        nav = tk.Frame(self, bg=Color.BG_APP)
        nav.pack(pady=(4, 14))

        self._prev_btn = tk.Button(
            nav,
            text="← Prev",
            font=("Arial", 11, "bold"),
            bg=Color.BG_BUTTON,
            fg=Color.FG_TEXT,
            activebackground=Color.BG_BUTTON_HOVER,
            activeforeground=Color.FG_TEXT,
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._step_back,
        )
        self._prev_btn.pack(side="left", padx=6)

        self._step_lbl = tk.Label(
            nav,
            text="",
            font=("Arial", 11),
            fg=Color.FG_TEXT,
            bg=Color.BG_APP,
            width=14,
        )
        self._step_lbl.pack(side="left", padx=8)

        self._next_btn = tk.Button(
            nav,
            text="Next →",
            font=("Arial", 11, "bold"),
            bg=Color.BG_BUTTON,
            fg=Color.FG_TEXT,
            activebackground=Color.BG_BUTTON_HOVER,
            activeforeground=Color.FG_TEXT,
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
        board_frame = tk.Frame(parent, bg=Color.BG_APP)
        board_frame.pack(side="left")
        rows, cols = BOARD_SIZE
        for i in range(rows):
            row_btns: list[tk.Button] = []
            for j in range(cols):
                pos = (i, j)
                is_dark = (i + j) % 2 == 1
                bg = Color.BG_BUTTON_DARK if is_dark else Color.BG_BUTTON
                self._tile_bg[pos] = bg
                color = ColorID(not is_dark)
                btn = tk.Button(
                    board_frame,
                    image=self._icons.get(color, self._icons.TILE),
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
        rows, cols = BOARD_SIZE

        for i in range(rows):
            for j in range(cols):
                pos = (i, j)
                if pos in snapshot:
                    color, ptype = snapshot[pos]
                    color = ColorID(color == "light")
                    ptype = self._icons.KING if ptype == "king" else self._icons.PAWN
                    image_key = (color, ptype)
                else:
                    is_dark = (i + j) % 2 == 1
                    color = ColorID(not is_dark)
                    image_key = (color, self._icons.TILE)
                self._tile_btns[i][j].configure(image=self._icons.get(*image_key))

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
