from enum import StrEnum, auto
from typing import Optional
from pathlib import Path

from PIL import Image, ImageTk
import tkinter as tk

from checkers.constants.colors import ColorID, Color
from checkers.user_interface.screen import Screen
from checkers.game.game import Game
from checkers.game.board import Tile
from checkers.game.pieces import Piece, King
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
        self.icons: dict[str, ImageTk.PhotoImage] = self.initialize_icons()

        self.tile_buttons: list[list[tk.Button]] = []
        self.board_frame: tk.Frame
        self.turn_var: tk.StringVar
        self.selected_tile: Optional[Tile] = None
        self.piece_jumps: dict[tuple[int, int], Optional[Piece]] = {}
        self.logs: list[str] = []

    def initialize_icons(self) -> dict[str, ImageTk.PhotoImage]:
        filepaths = {
            "light-tile": ASSET_DIRECTORY / "LightTile.png",
            "dark-tile": ASSET_DIRECTORY / "DarkTile.png",
            "dark-pawn": ASSET_DIRECTORY / "DarkPawn.png",
            "dark-king": ASSET_DIRECTORY / "DarkKing.png",
            "light-pawn": ASSET_DIRECTORY / "LightPawn.png",
            "light-king": ASSET_DIRECTORY / "LightKing.png",
        }
        scaled_images = (
            # Original 120x120
            (key, Image.open(path).resize((100, 100)))
            for key, path in filepaths.items()
        )
        return {key: ImageTk.PhotoImage(image) for key, image in scaled_images}

    def run(self) -> None:
        self.prompt_gamemode()
        if self.gamemode_type.get() == GameMode.PVP:
            self.prompt_player2_username()
        else:
            self.player2_username.set("CPU")
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

    def handle_username(self, flag: tk.BooleanVar, error_var: tk.StringVar) -> None:
        """Checks if input meets minimum requirements,
        notifies if it doesn't and boolean flag if met."""
        error_msg = auth_logic.validate_username(self.player2_username.get())
        if error_msg:
            error_var.set(error_msg)
            return
        flag.set(True)

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

    def init_game_labels(self) -> None:
        self.turn_var = tk.StringVar()
        self.update_turn()
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
                    image=self.get_image_from_(tile),
                    command=lambda position=tile.position: self.tile_clicked(position),
                )
                i, j = tile.position
                button.grid(row=i, column=j)
                current_row.append(button)
            self.tile_buttons.append(current_row)

    def get_image_from_(self, tile: Tile) -> tk.PhotoImage:
        if not tile.piece:
            color = "dark" if tile.color == ColorID.DARK else "light"
            key = f"{color}-tile"
            return self.icons[key]
        color = "dark" if tile.piece.color == ColorID.DARK else "light"
        piece_type = "king" if isinstance(tile.piece, King) else "pawn"
        key = f"{color}-{piece_type}"
        return self.icons[key]

    def tile_clicked(self, position: tuple[int, int]) -> None:
        """Handles essentially every part of the game logic"""
        tile = self.game._board._tile_at(position)
        original_tile = self.selected_tile
        valid_move_made = bool(
            self.selected_tile
            and self.selected_tile.piece
            and self.game.can_move_to(self.selected_tile.position, position)
        )
        forced_move_exists = bool(
            valid_move_made
            and tile.piece
            and any(self.game.get_valid_moves(tile.piece).values())
        )
        self.selected_tile = self.get_new_selected_state(tile, valid_move_made)
        self.update_tile_highlights(original_tile)
        if not valid_move_made:
            return
        # Log movement to list here
        self.move_piece(original_tile, tile)
        self.update_turn()

        if (winner := self.game.get_game_winner()) is not None:
            self.clear_screen()
            self.show_game_over_screen(winner)

    def get_new_selected_state(
        self, tile: Tile, valid_move_made: bool
    ) -> Optional[Tile]:
        """Updates the state of the selected tile and its highlighting."""
        if valid_move_made:
            return None
        if not tile.piece or tile.piece.color != self.game.turn:
            # Raise invalid tile message here
            return self.selected_tile
        if not self.selected_tile:
            return tile
        # Same tile pressed, deselect
        if tile is self.selected_tile:
            return None
        # Player presses on different piece it owns, switch to it
        if tile.piece.color == self.selected_tile.piece.color:
            return tile

    def update_tile_highlights(self, original_tile: Optional[Tile]) -> None:
        # Valid move made
        if original_tile and not self.selected_tile:
            self.toggle_highlighting(original_tile.position)
        # Invalid move made, do nothing
        elif original_tile is self.selected_tile:
            return
        # Empty selected tile
        elif not original_tile and self.selected_tile:
            self.toggle_highlighting(self.selected_tile.position)
        # Same tile pressed again
        elif original_tile and original_tile is self.selected_tile:
            self.toggle_highlighting(original_tile.position)
        # Player presses on different piece it owns, switch to it
        elif (
            self.selected_tile
            and original_tile.piece
            and self.selected_tile.piece
            and original_tile.piece.color == self.selected_tile.piece.color
        ):
            self.toggle_highlighting(original_tile.position)
            self.toggle_highlighting(self.selected_tile.position)

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
        self.piece_jumps = self.game.get_valid_moves(main_piece)
        for move_row, move_col in self.piece_jumps:
            move_button = self.tile_buttons[move_row][move_col]
            self._toggle_tile_highlight(move_button, moveset_color)

    def _toggle_tile_highlight(self, button: tk.Button, highlight_color: str) -> None:
        """Change highlighting using a given tkinter color."""
        if button["bg"] == highlight_color:
            highlight_color = "SystemButtonFace"  # default color
        button["bg"] = highlight_color

    def move_piece(self, old_tile: Tile, new_tile: Tile) -> None:
        self.game.move_piece(old_tile.position, new_tile.position)
        # Update tiles
        self.update_image(old_tile)
        self.update_image(new_tile)
        if captured_piece := self.piece_jumps[new_tile.position]:
            captured_tile = self.game._board._tile_at(captured_piece.position)
            self.update_image(captured_tile)
        # Log move
        move_type = "x" if captured_piece else "-"
        move = f"{old_tile.notation}{move_type}{new_tile.notation}"
        self.logs.append(move)

    def update_image(self, tile: Tile) -> None:
        row, col = tile.position
        button = self.tile_buttons[row][col]
        button["image"] = self.get_image_from_(tile)

    def update_turn(self) -> None:
        """Read game state's turn and updates turn UI accordingly"""
        username = self.get_username_by_color(self.game.turn)
        color = "BLACK" if self.game.turn == ColorID.DARK else "WHITE"
        self.turn_var.set(f"{color} ({username})")

    def get_username_by_color(self, color: ColorID) -> str:
        player1_is_dark = self.player1_username == self.dark_piece_player.get()
        color_is_dark = color == ColorID.DARK
        return (
            self.player1_username
            if player1_is_dark == color_is_dark
            else self.player2_username.get()
        )

    def show_game_over_screen(self, winner: ColorID) -> None:
        winner_username = self.get_username_by_color(winner)
        self.frame = tk.Frame()
        tk.Label(
            self,
            pady=100,
            text=f"INSERT SOME CONGRATULATIONS TO {winner_username}",
            font=("Comic Sans MS", 42),
        ).pack()
