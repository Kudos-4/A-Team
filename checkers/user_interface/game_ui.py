from enum import StrEnum, auto
from typing import Optional
from pathlib import Path

import tkinter as tk

from checkers.constants.colors import ColorID, Color
from checkers.user_interface.screen import Screen
from checkers.game.game import Game
from checkers.game.board import Tile
from checkers.auth import auth_logic

ASSET_DIRECTORY = Path("checkers") / "user_interface" / "assets"


class GameMode(StrEnum):
    PVP = auto()
    PVE = auto()


class GameScreen(Screen):
    def __init__(self, player1_username: str) -> None:
        super().__init__()

        self.player1_username = player1_username
        self.player2_username = tk.StringVar()
        self.dark_piece_player = tk.StringVar()
        self.gamemode_type = tk.StringVar()

        self.board_size = (8, 8)
        self.game = Game(self.board_size)

        self.tile_buttons: list[list[tk.Button]] = []
        filepaths = {
            "light": ASSET_DIRECTORY / "LightTile.png",
            "dark": ASSET_DIRECTORY / "DarkTile.png",
            "dark-pawn": ASSET_DIRECTORY / "DarkPawn.png",
            "dark-king": ASSET_DIRECTORY / "DarkKing.png",
            "light-pawn": ASSET_DIRECTORY / "LightPawn.png",
            "light-king": ASSET_DIRECTORY / "LightKing.png",
        }
        self.icons = {
            color: tk.PhotoImage(file=str(path)) for color, path in filepaths.items()
        }

        self.board_frame: tk.Frame
        self.turn_var: tk.StringVar
        self.selected_tile: Optional[Tile] = None
        # Piece notation: 9-14, 23x14
        # Piece move: '-'
        # Piece captures 'x'
        self.logs: list[tuple[int, str, int]] = []

    def run(self) -> None:
        self.prompt_gamemode()
        if self.gamemode_type.get() == GameMode.PVP:
            self.prompt_player2_username()
        else:
            self.player2_username.set("Computer")
        self.prompt_whos_first()
        self.configure(background=Color.CHARCOAL)
        self.init_game_labels()
        self.init_board()

    def prompt_gamemode(self) -> None:
        """Create UI for selecting gamemode. When player clicks on button
        modify mutable gamemode_type to update state and continue to start_game()"""

        labels = (
            "HOW WOULD YOU LIKE TO DIE 😈",
            '"I WANT TO DIE BY THE CHECKER\'S VERSION OF UHHHHH...."',
        )
        for label in labels:
            tk.Label(
                self,
                text=label,
                font=("Comic Sans MS", 42),
            ).pack(pady=75)

        button_frame = tk.Frame(self)
        options = (
            ("GARRY KASPAROV", GameMode.PVP),
            ("DEEP BLUE", GameMode.PVE),
        )
        for option, gamemode in options:
            new_button = tk.Button(
                button_frame,
                text=option,
                font=("Arial", 46),
                # mode=gamemode required or else both point to same reference
                # gamemode was recently assigned (PVE)
                command=lambda mode=gamemode: self.gamemode_type.set(mode),
            )
            new_button.grid(pady=20, sticky="nsew")
        button_frame.pack()

        self.wait_variable(self.gamemode_type)
        self.clear_screen()

    def prompt_player2_username(self) -> None:
        frame = tk.Frame(self)
        frame.pack()
        tk.Label(
            frame,
            text="Enter player 2's username below",
            font=("Arial", 28, "bold"),
        ).pack(pady=20, anchor="center")

        username_flag = tk.BooleanVar()
        error_var = tk.StringVar()

        tk.Entry(
            frame,
            textvariable=self.player2_username,
            font=("Arial", 18),
            width=28,
        ).pack()

        tk.Button(
            frame,
            text="Submit username",
            command=lambda: self.handle_username(username_flag, error_var),
        ).pack()

        tk.Label(frame, textvariable=error_var, font=("Arial", 18)).pack()

        self.wait_variable(username_flag)
        self.clear_screen()

    def prompt_whos_first(self) -> None:
        """Ask who plays the first move (as black)."""
        frame = tk.Frame(self)
        frame.pack()
        tk.Label(
            frame,
            text="Who plays first as black?",
            font=("Arial", 28, "bold"),
        ).pack(pady=20, anchor="center")

        tk.Button(
            frame,
            text=self.player1_username,
            font=("Arial", 18),
            command=lambda: self.dark_piece_player.set(self.player1_username),
        ).pack(pady=20, anchor="center")
        tk.Button(
            frame,
            text=self.player2_username.get(),
            font=("Arial", 18),
            command=lambda: self.dark_piece_player.set(self.player2_username.get()),
        ).pack(pady=20, anchor="center")

        self.wait_variable(self.dark_piece_player)
        self.clear_screen()

    def handle_username(self, flag: tk.BooleanVar, error_var: tk.StringVar) -> None:
        """Checks if input meets minimum requirements,
        notifies if it doesn't and boolean flag if met."""
        error_msg = auth_logic.validate_username(self.player2_username.get())
        if error_msg:
            error_var.set(error_msg)
            return
        flag.set(True)

    def init_game_labels(self) -> None:
        self.turn_var = tk.StringVar(value=f"BLACK ({self.dark_piece_player.get()})")
        tk.Label(self, text="Current Turn:").pack(anchor="nw")
        tk.Label(self, textvariable=self.turn_var).pack(anchor="nw")

    def init_board(self) -> None:
        """Creates board visuals and each tiles' functions"""
        self.board_frame = tk.Frame(self)
        self.board_frame.place(relx=0.5, rely=0.5, anchor="center")
        for row in self.game._board._board:
            current_row: list[tk.Button] = []
            for tile in row:
                button = tk.Button(
                    self.board_frame,
                    image=self.get_image_at_(tile),
                    command=lambda position=tile.position: self.tile_clicked(position),
                )
                i, j = tile.position
                button.grid(row=i, column=j)
                current_row.append(button)
            self.tile_buttons.append(current_row)

    def get_image_at_(self, tile: Tile) -> tk.PhotoImage:
        if not tile.piece:
            key = "dark" if tile.color == ColorID.DARK else "light"
            return self.icons[key]
        color = "dark" if tile.piece.color == ColorID.DARK else "light"
        key = color + "-pawn"
        return self.icons[key]

    def tile_clicked(self, position: tuple[int, int]) -> None:
        """Handles essentially every part of the game logic"""
        tile = self.game._board._tile_at(position)
        valid_move_made = bool(
            self.selected_tile
            and self.selected_tile.piece
            and self.game.can_move_to(self.selected_tile.position, position)
        )
        self.get_new_selected_state(tile, valid_move_made)
        if not valid_move_made:
            return
        # Log movement to list here

    def get_new_selected_state(self, tile: Tile, valid_move_made: bool) -> None:
        """Updates the state of the selected tile and its highlighting."""
        if valid_move_made:
            print(f"Move made from {self.selected_tile.position} to {tile.position}.")
            self.toggle_highlighting(self.selected_tile.position)
            self.selected_tile = None
        elif not tile.piece or tile.piece.color != self.game.turn:
            print(f"Invalid tile at {tile.position} pressed.")
            # Raise invalid tile message here
            return
        elif not self.selected_tile:
            print(f"Tile at {tile.position} highlighted.")
            self.selected_tile = tile
            self.toggle_highlighting(tile.position)
        # Same tile pressed, deselect
        elif tile is self.selected_tile:
            print(f"Tile at {tile.position} deselected.")
            self.selected_tile = None
            self.toggle_highlighting(tile.position)
        # Player presses on different piece it owns, switch to it
        elif tile.piece.color == self.selected_tile.piece.color:
            print(f"Tile at {self.selected_tile.position} switched to {tile.position}.")
            self.toggle_highlighting(self.selected_tile.position)
            self.selected_tile = None
            self.tile_clicked(tile.position)

    def toggle_highlighting(
        self,
        position: tuple[int, int],
        piece_highlight: str = "lime green",
        moveset_color: str = "yellow",
    ) -> None:
        """Toggle a tile's and its possible moves' highlight colors"""
        # Highlight main piece
        row, col = position
        main_button = self.tile_buttons[row][col]
        self._toggle_tile_highlight(main_button, piece_highlight)
        # Highlight main piece's moves
        main_piece = self.game._board[position]
        for move_row, move_col in self.game.get_valid_moves(main_piece):
            move_button = self.tile_buttons[move_row][move_col]
            self._toggle_tile_highlight(move_button, moveset_color)

    def _toggle_tile_highlight(self, button: tk.Button, highlight_color: str) -> None:
        """Change highlighting of a given tkinter color."""
        if button["bg"] == highlight_color:
            highlight_color = "SystemButtonFace"  # default color
        button.config(bg=highlight_color)
