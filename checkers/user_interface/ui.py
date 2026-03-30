from typing import Callable, Any
from enum import StrEnum, auto

import tkinter as tk

from checkers.game.game import Game


class GameMode(StrEnum):
    PVP = auto()
    PVE = auto()


class CheckersUserInterface(tk.Tk):
    def __init__(self, resolution: tuple[int, int]) -> None:
        super().__init__()
        self.width, self.height = resolution
        # Geometry takes in a string for resolution
        self.resolution_str = f"{self.width}x{self.height}"
        self.geometry(self.resolution_str)
        self.attributes("-fullscreen", True)
        self.main_menu()

    def main_menu(self) -> None:
        self.title("Main Menu")  # Window name
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
            ("USER INFO", self.open_login),
            ("GET ME OUTTA HEEREERERERE 🏃", self.destroy),
        )

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
        self, title: str = "", enable_fullscreen: bool = False
    ) -> tk.Toplevel:
        """Hides main menu and creates a new window to work off of."""
        self.withdraw()  # Hide function
        window = tk.Toplevel()
        window.title(title)
        window.geometry(self.resolution_str)
        window.attributes("-fullscreen", enable_fullscreen)
        return window

    def open_game_history(self) -> None:
        print("open_game_history Not implemented")

    def open_login(self) -> None:
        print("open_login Not implemented")

    def open_new_game(self) -> None:
        """Opens a new window instance of a checkers game."""
        window_name = "🦅AMERICAN CHECKERS RAHHHHH🔫"
        game_window = self.switch_to_new_window(window_name)

        gamemode = tk.StringVar()
        self.prompt_gamemode(game_window, gamemode)

        config: dict[str, Any] = {
            "board-size": (8, 8),
            "game-mode": gamemode.get(),
        }
        self.start_game(game_window, config)

        self.wait_window(game_window)
        self.wm_deiconify()

    def prompt_gamemode(
        self,
        window: tk.Toplevel,
        gamemode_type: tk.StringVar,
    ) -> None:
        """Create UI for selecting gamemode. When player clicks on button
        modify mutable gamemode_type to update state and continue to start_game()"""

        def update_gamemode(gamemode: GameMode) -> Callable:
            return lambda: gamemode_type.set(gamemode)

        tk.Label(
            window,
            text="HOW WOULD YOU LIKE TO DIE 😈",
            font=("Comic Sans MS", 42),
            pady=10,
        ).pack()
        tk.Label(
            window,
            text="I WANT TO DIE BY THE CHECKER'S VERSION OF UHHHHH....",
            font=("Comic Sans MS", 42),
        ).pack(pady=50)

        button_frame = tk.Frame(window)
        button_frame.columnconfigure(0)
        button_frame.columnconfigure(1)
        choices = (
            ("GARRY KASPAROV", GameMode.PVP),
            ("DEEP BLUE", GameMode.PVE),
        )
        for i, (option, gamemode) in enumerate(choices):
            new_button = tk.Button(
                button_frame,
                text=option,
                font=("Arial", 28),
                # Don't simplify helper function to single lambda
                # Both will refer to gamemode variable; both will be GameMode.PVE
                # update_gamemode() called during loop & standard lambda doesn't
                command=update_gamemode(gamemode),
            )
            new_button.grid(padx=100, pady=40, row=0, column=i, sticky="W")
        button_frame.pack(padx=10)

        window.wait_variable(gamemode_type)
        for widget in tuple(window.children.values()):
            widget.destroy()

    def start_game(self, window: tk.Toplevel, configs: dict[str, Any]) -> None:
        game = Game(configs["board-size"])
        game._board.print_positions()
