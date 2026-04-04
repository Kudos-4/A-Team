from __future__ import annotations
from enum import StrEnum, auto

import tkinter as tk

from checkers.user_interface.screen import Screen
from checkers.game.game import Game
from checkers.game.board import Tile
from checkers.constants.colors import ColorID, Color
from checkers.auth import auth_logic


class GameMode(StrEnum):
    PVP = auto()
    PVE = auto()


class GameScreen(Screen):
    def __init__(self) -> None:
        super().__init__()

        self.gamemode_type = tk.StringVar()
        self.player2_user = tk.StringVar()
        self.board_size = (8, 8)
        self.game = Game(self.board_size)

        self.tiles: list[list[tk.Button]] = []
        filepaths = {
            "light": r"checkers\user_interface\assets\LightTile.png",
            "dark": r"checkers\user_interface\assets\DarkTile.png",
            "dark-pawn": r"checkers\user_interface\assets\DarkPawn.png",
            "dark-king": r"checkers\user_interface\assets\DarkKing.png",
            "light-pawn": r"checkers\user_interface\assets\LightPawn.png",
            "light-king": r"checkers\user_interface\assets\LightKing.png",
        }
        self.icons = {
            color: tk.PhotoImage(file=path) for color, path in filepaths.items()
        }

        # Not initialized because clear_screen() will remove it
        self.frame: tk.Frame
        self.turn_var: tk.StringVar

    def run(self) -> None:
        self.prompt_gamemode()
        if self.gamemode_type.get() == GameMode.PVP:
            self.prompt_player2_user()
        else:
            self.player2_user.set("Computer")
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

    def prompt_player2_user(self) -> None:
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
            textvariable=self.player2_user,
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
        error_msg = auth_logic.validate_username(self.player2_user.get())
        if error_msg:
            error_var.set(error_msg)
            return
        flag.set(True)

    def init_game_labels(self) -> None:
        turn = "BLACK" if self.game.turn == ColorID.DARK else "WHITE"
        self.turn_var = tk.StringVar(value=f"Current Turn: {turn}")
        label = tk.Label(self, textvariable=self.turn_var)
        label.pack(anchor="nw")

    def init_board(self) -> None:
        """Creates board visuals and its cells' functions"""
        self.frame = tk.Frame(self)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        for row in self.game._board._board:
            current_row: list[tk.Button] = []
            for tile in row:
                button = tk.Button(
                    self.frame,
                    image=self.get_image_at_(tile),
                    command=lambda position=tile.position: self.tile_clicked(position),
                )
                i, j = tile.position
                button.grid(row=i, column=j)
                current_row.append(button)
            self.tiles.append(current_row)

    def get_image_at_(self, tile: Tile) -> tk.PhotoImage:
        if not tile.piece:
            key = "dark" if tile.color == ColorID.DARK else "light"
            return self.icons[key]
        color = "dark" if tile.piece.color == ColorID.DARK else "light"
        key = color + "-pawn"
        return self.icons[key]

    def tile_clicked(self, position: tuple[int, int]) -> None:
        """Handles essentially every part of the game logic"""
        print(f"Tile pressed at {position}")
