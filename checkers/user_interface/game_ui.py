"""Game UI that sets a GameMode and update itself after each input."""

from typing import Optional
from enum import StrEnum, auto
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageTk
from tkinter import messagebox
import tkinter as tk

from checkers.constants.colors import ColorID
from checkers.user_interface.screen import Screen
from checkers.game.game import Game
from checkers.game.pieces import King
from checkers.gamemodes.gamemode import GameMode
from checkers.gamemodes.pvp import PvPGameMode
from checkers.auth import auth_logic
from checkers.auth.database import save_game

ASSET_DIRECTORY = Path("checkers") / "user_interface" / "assets"
GAME_HISTORY_PATH = Path("checkers") / "game_history.json"


class GameModeType(StrEnum):
    PVP = auto()
    PVE = auto()


class GameScreen(Screen):
    """Main game UI screen for checkers."""

    def __init__(self, player1_username: str, user_id: int) -> None:
        super().__init__()

        # Theme colors
        self.BG_APP = "#0f172a"
        self.BG_TOPBAR = "#111827"
        self.BG_CARD = "#1e293b"
        self.BG_PANEL = "#233247"
        self.BG_BUTTON = "#334155"
        self.BG_BUTTON_HOVER = "#475569"
        self.BG_DANGER = "#f43f5e"
        self.BG_DANGER_HOVER = "#e11d48"
        self.FG_TEXT = "#f8fafc"
        self.FG_MUTED = "#94a3b8"
        self.FG_ACCENT = "#f43f5e"

        # Highlight colors
        self.HL_SELECTED = "#3b82f6"
        self.HL_MOVES = "#60a5fa"
        self.HL_FORCED = "#f59e0b"

        # Session/game metadata
        self.player1_username = player1_username
        self.user_id = user_id
        self.player2_username: str = "Computer"

        # Setup state vars
        self.dark_piece_player = tk.StringVar()
        self.gamemode_type = tk.StringVar()
        self.turn = tk.StringVar()

        # Game engine and board state
        self.board_size = (8, 8)
        self.game: Game
        self.game_handler: GameMode
        self.icons = self.initialize_icons()
        self.tile_buttons: list[list[tk.Button]] = []
        self.tile_default_bg: dict[tuple[int, int], str] = {}

        self.logs: list[str] = []
        self.start_date: datetime

        # Lockout state is managed by auth flow, not here
        self.configure(bg=self.BG_APP)

    def initialize_icons(self) -> dict[str, ImageTk.PhotoImage]:
        """Load and scale all board and piece images."""
        filepaths = {
            "light-tile": ASSET_DIRECTORY / "LightTile.png",
            "dark-tile": ASSET_DIRECTORY / "DarkTile.png",
            "dark-pawn": ASSET_DIRECTORY / "DarkPawn.png",
            "dark-king": ASSET_DIRECTORY / "DarkKing.png",
            "light-pawn": ASSET_DIRECTORY / "LightPawn.png",
            "light-king": ASSET_DIRECTORY / "LightKing.png",
        }

        icons: dict[str, ImageTk.PhotoImage] = {}
        for key, path in filepaths.items():
            image = Image.open(path).resize((92, 92))
            icons[key] = ImageTk.PhotoImage(image)
        return icons

    def run(self) -> None:
        """Initialize a new game session and render UI."""
        self.clear_screen()
        self.configure(bg=self.BG_APP)

        self.player2_username = "Computer"
        self.dark_piece_player.set("")
        self.gamemode_type.set("")
        self.turn.set("")

        self.game = Game(self.board_size)
        self.tile_buttons = []
        self.tile_default_bg = {}
        self.logs = []

        self.prompt_gamemode()
        if self.gamemode_type.get() == GameModeType.PVP:
            self.prompt_player2_username()
            self.game_handler = PvPGameMode(self.game)
        else:
            # self.game_handler = PvEGameMode(self.game)
            raise NotImplementedError("No PvE gamemode implemented.")
        self.prompt_whos_first()

        self.start_date = datetime.now()
        self._build_game_layout()
        self.update_turn_ui()
        self._show_forced_moves()

    # -------------------------------------------------------------------------
    # Pre-game prompts
    # -------------------------------------------------------------------------

    def prompt_gamemode(self) -> None:
        """Prompt player to select game mode."""
        self.clear_screen()
        self.configure(bg=self.BG_APP)

        card = self._create_center_card()

        tk.Label(
            card,
            text="SELECT MODE",
            font=("Arial", 30, "bold"),
            fg=self.FG_ACCENT,
            bg=self.BG_CARD,
        ).pack(pady=(0, 8))

        tk.Label(
            card,
            text="How would you like to play?",
            font=("Arial", 12),
            fg=self.FG_MUTED,
            bg=self.BG_CARD,
        ).pack(pady=(0, 18))

        self._themed_button(
            card,
            text="Player vs Player",
            command=lambda: self.gamemode_type.set(GameModeType.PVP),
        ).pack(fill="x", pady=6)

        self._themed_button(
            card,
            text="Player vs Computer",
            command=lambda: self.gamemode_type.set(GameModeType.PVE),
        ).pack(fill="x", pady=6)

        self.wait_variable(self.gamemode_type)

    def prompt_player2_username(self) -> None:
        """Prompt player 2 username for PvP mode."""
        self.clear_screen()
        self.configure(bg=self.BG_APP)

        card = self._create_center_card()

        tk.Label(
            card,
            text="PLAYER 2",
            font=("Arial", 28, "bold"),
            fg=self.FG_ACCENT,
            bg=self.BG_CARD,
        ).pack(pady=(0, 8))

        tk.Label(
            card,
            text="Enter player 2's username",
            font=("Arial", 12),
            fg=self.FG_MUTED,
            bg=self.BG_CARD,
        ).pack(pady=(0, 16))

        username = tk.StringVar()
        valid_username = tk.BooleanVar(value=False)
        error_var = tk.StringVar(value="")

        entry = tk.Entry(
            card,
            textvariable=username,
            font=("Arial", 14),
            bg=self.BG_PANEL,
            fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT,
            bd=0,
            highlightthickness=2,
            highlightbackground=self.BG_CARD,
            highlightcolor=self.FG_ACCENT,
            width=28,
        )
        entry.pack(ipady=8, pady=(0, 10))
        entry.focus_set()

        tk.Label(
            card,
            textvariable=error_var,
            font=("Arial", 10),
            fg="#ef4444",
            bg=self.BG_CARD,
            wraplength=420,
        ).pack(pady=(0, 10))

        self._themed_button(
            card,
            text="Confirm Username",
            command=lambda: self.handle_username(username, valid_username, error_var),
        ).pack(fill="x")

        self.wait_variable(valid_username)

    def handle_username(
        self, username: tk.StringVar, flag: tk.BooleanVar, error_var: tk.StringVar
    ) -> None:
        """Validate player 2 username and continue only if valid."""
        error_msg = auth_logic.validate_username(username.get().strip())
        if error_msg:
            error_var.set(error_msg)
            return
        self.player2_username = username.get().strip()
        flag.set(True)

    def prompt_whos_first(self) -> None:
        """Prompt who plays first as dark."""
        self.clear_screen()
        self.configure(bg=self.BG_APP)

        card = self._create_center_card()

        tk.Label(
            card,
            text="FIRST MOVE",
            font=("Arial", 28, "bold"),
            fg=self.FG_ACCENT,
            bg=self.BG_CARD,
        ).pack(pady=(0, 8))

        tk.Label(
            card,
            text="Who starts as DARK?",
            font=("Arial", 12),
            fg=self.FG_MUTED,
            bg=self.BG_CARD,
        ).pack(pady=(0, 16))

        self._themed_button(
            card,
            text=self.player1_username,
            command=lambda: self.dark_piece_player.set(self.player1_username),
        ).pack(fill="x", pady=6)

        self._themed_button(
            card,
            text=self.player2_username,
            command=lambda: self.dark_piece_player.set(self.player2_username),
        ).pack(fill="x", pady=6)

        self.wait_variable(self.dark_piece_player)

    # -------------------------------------------------------------------------
    # Main game layout
    # -------------------------------------------------------------------------

    def _build_game_layout(self) -> None:
        """Build main game screen: top bar, side panel, and board."""
        self.clear_screen()
        self.configure(bg=self.BG_APP)

        # Top bar
        top_bar = tk.Frame(self, bg=self.BG_TOPBAR)
        top_bar.pack(fill="x", padx=14, pady=(10, 0))

        tk.Label(
            top_bar,
            text=f"{self.player1_username} vs {self.player2_username}",
            font=("Arial", 12, "bold"),
            fg=self.FG_MUTED,
            bg=self.BG_TOPBAR,
            padx=10,
            pady=8,
        ).pack(side="left")

        tk.Label(
            top_bar,
            textvariable=self.turn,
            font=("Arial", 12, "bold"),
            fg=self.FG_TEXT,
            bg=self.BG_TOPBAR,
            padx=10,
            pady=8,
        ).pack(side="right")

        # Main body
        body = tk.Frame(self, bg=self.BG_APP)
        body.pack(fill="both", expand=True, padx=18, pady=16)

        # Side panel
        panel = tk.Frame(body, bg=self.BG_CARD, padx=16, pady=16)
        panel.pack(side="left", fill="y")

        tk.Label(
            panel,
            text="Match Controls",
            font=("Arial", 14, "bold"),
            fg=self.FG_ACCENT,
            bg=self.BG_CARD,
        ).pack(anchor="w", pady=(0, 12))

        self._themed_button(
            panel,
            text="Offer Draw",
            command=self.end_in_draw,
            bg=self.BG_BUTTON,
            hover_bg=self.BG_BUTTON_HOVER,
        ).pack(fill="x", pady=6)

        self._themed_button(
            panel,
            text="Return to Menu",
            command=self._confirm_exit_match,
            bg=self.BG_DANGER,
            hover_bg=self.BG_DANGER_HOVER,
        ).pack(fill="x", pady=6)

        tk.Label(
            panel,
            text="Move Log",
            font=("Arial", 12, "bold"),
            fg=self.FG_MUTED,
            bg=self.BG_CARD,
        ).pack(anchor="w", pady=(18, 8))

        self.log_text = tk.Text(
            panel,
            width=28,
            height=20,
            bg=self.BG_PANEL,
            fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT,
            bd=0,
            relief="flat",
            padx=10,
            pady=10,
            state="disabled",
            font=("Consolas", 10),
        )
        self.log_text.pack(fill="both", expand=False)

        # Board area
        board_wrap = tk.Frame(body, bg=self.BG_APP)
        board_wrap.pack(side="left", fill="both", expand=True)

        self._init_board(board_wrap)

    def _init_board(self, parent: tk.Widget) -> None:
        """Create all board tiles and bind click handlers."""
        board_frame = tk.Frame(parent, bg=self.BG_APP)
        board_frame.pack(expand=True)  # 不用 place，避免尺寸计算问题

        self.tile_buttons = []
        self.tile_default_bg = {}

        # 用固定 8x8 + _tile_at 取格子，避免内部结构差异导致循环空
        for i in range(8):
            current_row: list[tk.Button] = []
            for j in range(8):
                # tile = self.game._board._tile_at((i, j))
                position = (i, j)
                tile_color = self.game.get_tile_color_at(position)

                base_bg = "#1f2937" if tile_color == ColorID.DARK else "#334155"
                self.tile_default_bg[(i, j)] = base_bg

                button = tk.Button(
                    board_frame,
                    image=self._get_image(position),
                    bg=base_bg,
                    activebackground=base_bg,
                    bd=0,
                    relief="flat",
                    cursor="hand2",
                    command=lambda pos=(i, j): self.tile_clicked(pos),
                )
                button.grid(row=i, column=j, padx=1, pady=1)
                current_row.append(button)
            self.tile_buttons.append(current_row)

    # -------------------------------------------------------------------------
    # Board rendering and interactions
    # -------------------------------------------------------------------------

    def _get_image(self, position: tuple[int, int]) -> ImageTk.PhotoImage:
        """Resolve the image for a tile based on piece and tile type."""
        if piece := self.game.get_piece_at(position):
            color = "dark" if piece.color == ColorID.DARK else "light"
            piece_type = "king" if isinstance(piece, King) else "pawn"
            return self.icons[f"{color}-{piece_type}"]

        tile_color = self.game.get_tile_color_at(position)
        color = "dark" if tile_color == ColorID.DARK else "light"
        return self.icons[f"{color}-tile"]

    def tile_clicked(self, position: tuple[int, int]) -> None:
        """Send user input to GameMode handler, and update UI afterwards"""
        self.game_handler.tile_pressed(position)  # Updates game state

        self._clear_all_highlights()
        if selected_position := self.game_handler.get_selected():
            self._highlight_selected_and_moves(selected_position)
        self._show_forced_moves()
        
        if not self.game_handler.get_valid_move_made():
            return
        old, capture, new = self.game_handler.get_previous_move()
        updated_tiles = (old, capture, new) if capture else (old, new)
        self.update_tile_images(*updated_tiles)
        self.update_turn_ui()
        self.update_logging(old, capture, new)

        winner = self.game.get_game_winner()
        if winner is None:
            return
        winner_username = self.get_username_by_color(winner)
        self.export_result_to_database(winner_username)
        self.show_end_screen(winner_username)

    def update_tile_images(self, *positions: tuple[int, int]) -> None:
        """Iterates over each position, updating the tile type at each one."""
        for position in positions:
            row, col = position
            button = self.tile_buttons[row][col]
            button["image"] = self._get_image(position)

    def update_logging(
        self,
        old: tuple[int, int],
        capture: Optional[tuple[int, int]],
        new: tuple[int, int],
    ) -> None:
        """Writes to both the log list and log ingame UI."""
        move_type = "x" if capture else "-"
        old_notation = self.game.get_notation_at(old)
        new_notation = self.game.get_notation_at(new)
        move = f"{old_notation}{move_type}{new_notation}"
        self.logs.append(move)
        self._append_log_line(move)

    def _highlight_selected_and_moves(self, position: tuple[int, int]) -> None:
        """Highlight selected piece and all valid target moves."""
        self._set_tile_bg(position, self.HL_SELECTED)

        main_piece = self.game._board[position]
        assert main_piece
        for piece_position in self.game.get_valid_moves(main_piece):
            self._set_tile_bg(piece_position, self.HL_MOVES)

    def _show_forced_moves(self) -> None:
        """Highlight forced jump pieces for current turn."""
        for forced_position in self.game.get_all_jumps(self.game.turn):
            # Do not overwrite currently selected tile color
            selected = self.game_handler.get_selected()
            if selected and forced_position == selected:
                continue
            self._set_tile_bg(forced_position, self.HL_FORCED)

    def _clear_all_highlights(self) -> None:
        """Restore all tile button backgrounds to default colors."""
        for i, row in enumerate(self.tile_buttons):
            for j, button in enumerate(row):
                base_bg = self.tile_default_bg[(i, j)]
                button.configure(bg=base_bg, activebackground=base_bg)

    def _set_tile_bg(self, position: tuple[int, int], color: str) -> None:
        """Set a tile's background highlight color."""
        row, col = position
        button = self.tile_buttons[row][col]
        button.configure(bg=color, activebackground=color)

    def _append_log_line(self, move: str) -> None:
        """Append one line to side move log."""
        if not hasattr(self, "log_text"):
            return
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{len(self.logs):>3}. {move}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def update_turn_ui(self) -> None:
        """Update turn text in top bar."""
        color_name = "BLACK" if self.game.turn == ColorID.DARK else "WHITE"
        username = self.get_username_by_color(self.game.turn)
        self.turn.set(f"Turn: {color_name} ({username})")

    def get_username_by_color(self, color: ColorID) -> str:
        """Return username by piece color assignment."""
        player1_is_dark = self.player1_username == self.dark_piece_player.get()
        color_is_dark = color == ColorID.DARK
        return (
            self.player1_username
            if player1_is_dark == color_is_dark
            else self.player2_username
        )

    # -------------------------------------------------------------------------
    # End game and persistence
    # -------------------------------------------------------------------------

    def end_in_draw(self) -> None:
        """End game as draw and show final screen."""
        if self.logs:
            self.export_result_to_database(None)
        self.show_end_screen(None)

    def export_result_to_database(self, winner: Optional[str]) -> None:
        """Persist game result to database."""
        if winner:
            outcome = "Win" if winner == self.player1_username else "Loss"
        else:
            outcome = "Draw"

        # Save database history
        save_game(
            user_id=self.user_id,
            opponent_name=self.player2_username,
            result=outcome,
            total_moves=len(self.logs),
            moves=self.logs,
            played_at=self.start_date.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def show_end_screen(self, winner: Optional[str]) -> None:
        """Render final result screen with actions."""
        self.clear_screen()
        self.configure(bg=self.BG_APP)

        card = self._create_center_card()

        if winner:
            winner_text = f"🏆 Congratulations, {winner}!"
            detail_text = f"Game finished in {len(self.logs)} move(s)."
            color = "#22c55e"
        else:
            winner_text = "🤝 Draw!"
            detail_text = f"Game ended in a draw after {len(self.logs)} move(s)."
            color = "#f59e0b"

        tk.Label(
            card,
            text=winner_text,
            font=("Arial", 28, "bold"),
            fg=color,
            bg=self.BG_CARD,
        ).pack(pady=(0, 8))

        tk.Label(
            card,
            text=detail_text,
            font=("Arial", 12),
            fg=self.FG_MUTED,
            bg=self.BG_CARD,
        ).pack(pady=(0, 20))

        self._themed_button(
            card,
            text="Start New Round",
            command=self.run,
        ).pack(fill="x", pady=6)

        self._themed_button(
            card,
            text="Return to Menu",
            command=self.destroy,
            bg=self.BG_DANGER,
            hover_bg=self.BG_DANGER_HOVER,
        ).pack(fill="x", pady=6)

    def _confirm_exit_match(self) -> None:
        """Ask user before leaving an ongoing game."""
        should_exit = messagebox.askyesno(
            "Return to Menu",
            "Are you sure you want to leave this match?\nCurrent progress will be lost.",
        )
        if should_exit:
            self.destroy()

    # -------------------------------------------------------------------------
    # UI helpers
    # -------------------------------------------------------------------------

    def _create_center_card(self) -> tk.Frame:
        """Create a centered card container."""
        container = tk.Frame(self, bg=self.BG_APP)
        container.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(container, bg=self.BG_CARD, padx=36, pady=30)
        card.pack()
        return card

    def _themed_button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        bg: Optional[str] = None,
        hover_bg: Optional[str] = None,
    ) -> tk.Button:
        """Create a theme-consistent button with hover effect."""
        base_bg = bg or self.BG_BUTTON
        over_bg = hover_bg or self.BG_BUTTON_HOVER

        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 12, "bold"),
            bg=base_bg,
            fg=self.FG_TEXT,
            activebackground=over_bg,
            activeforeground=self.FG_TEXT,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=10,
            command=command,
        )
        btn.bind("<Enter>", lambda _e: btn.configure(bg=over_bg))
        btn.bind("<Leave>", lambda _e: btn.configure(bg=base_bg))
        return btn
