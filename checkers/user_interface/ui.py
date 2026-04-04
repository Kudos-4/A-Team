from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Optional
from enum import StrEnum, auto

import tkinter as tk
import datetime

from checkers.game.game import Game
from checkers.game.board import Tile
from checkers.constants.colors import ColorID
from checkers.user_interface.auth_ui import AuthUI


class CheckersUserInterface(tk.Tk):
    def __init__(self, resolution: tuple[int, int]) -> None:
        super().__init__()
        self.width, self.height = resolution
        # Geometry takes in a string for resolution
        self.resolution_str = f"{self.width}x{self.height}"
        self.geometry(self.resolution_str)
        self.attributes("-fullscreen", True)

        # Track logged-in user
        self.current_user: Optional[str] = None

        # Clock
        self._datetime_var = tk.StringVar()
        self.tick_datetime()

        # Call AuthUI to handle login and register
        self._auth = AuthUI(self, on_login_success=self.login_success)
        # Show login screen before main menu
        self._auth.show_login()

    def login_success(self, username: str) -> None:
        """
        Shared with auth_ui.py.
        Called by AuthUI when login succeeds -> show main menu.
        """
        self.current_user = username
        self.main_menu()

    def main_menu(self) -> None:
        self.title("Main Menu")  # Window name

        # Clear any existing widgets (login screen)
        for widget in self.winfo_children():
            widget.destroy()

        # Top bar: datetime (left) | username (right)
        top_bar = tk.Frame(self)
        top_bar.pack(fill="x", padx=16, pady=(8, 0))

        # datetime
        tk.Label(
            top_bar,
            textvariable=self._datetime_var,
            font=("Arial", 16),
            anchor="w",
        ).pack(side="left")

        # username
        tk.Label(
            top_bar,
            text=f"👤  {self.current_user}",
            font=("Arial", 16, "bold"),
            anchor="e",
        ).pack(side="right")

        menu_title_label = tk.Label(
            self,
            text="Welcome to Checker HELL!!( •̀ ω •́ )y",
            font=("Comic Sans MS", 42),
            pady=10,
        )
        menu_title_label.pack()

        self.create_menu_buttons(
            ("I WANNA PLAY AND LOSE AGAIN!! (╯▔皿▔)╯", self.open_new_game),
            ("GAME HISTORY", self.open_game_history),
            ("LOG OUT", self.handle_logout),
            ("GET ME OUTTA HEEREERERERE 🏃", self.destroy),
        )

    def handle_logout(self) -> None:
        """Clear session and return to login screen."""
        self.current_user = None
        self._auth.show_login()

    def tick_datetime(self) -> None:
        """Update the shared clock variable every second."""
        now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self._datetime_var.set(now)
        self.after(1000, self.tick_datetime)

    def create_menu_buttons(self, *args: tuple[str, Callable]) -> None:
        """Attaches newly created buttons to button_frame"""
        button_frame = tk.Frame(self)
        for button_name, action in args:
            new_button = tk.Button(
                button_frame,
                text=button_name,
                font=("Arial", 36),
                command=action,
            )
            # Sticky: Alignment (North, South, East, West)
            new_button.grid(pady=12, sticky="W")
        button_frame.pack(padx=10, side="left")

    def switch_to_new_window(
        self,
        screen_type: type[Screen],
        title: str = "",
        enable_fullscreen: bool = True,
    ) -> Screen:
        """Hides main menu and creates a new window to work off of."""
        self.withdraw()  # Hide function
        window = screen_type()
        window.title(title)
        window.geometry(self.resolution_str)
        window.attributes("-fullscreen", enable_fullscreen)
        return window

    def open_game_history(self) -> None:
        print("open_game_history Not implemented")

    def open_new_game(self) -> None:
        """Opens a new window instance of a checkers game."""
        window_name = "🦅AMERICAN CHECKERS RAHHHHH🔫"
        game_window = self.switch_to_new_window(GameScreen, window_name)
        game_window.run()
        self.wait_window(game_window)
        self.wm_deiconify()


class Screen(tk.Toplevel, ABC):
    def clear_screen(self) -> None:
        """Remove all widgets on screen"""
        for widget in tuple(self.children.values()):
            widget.destroy()

    @abstractmethod
    def run(self) -> None:
        """Acts as the injection point to run the new window"""
        pass


class GameMode(StrEnum):
    PVP = auto()
    PVE = auto()


class GameScreen(Screen):
    def __init__(self) -> None:
        super().__init__()

        self.gamemode_type = tk.StringVar()
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

    def run(self) -> None:
        self.prompt_gamemode()
        self.initialize_board()

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

    def initialize_board(self) -> None:
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
