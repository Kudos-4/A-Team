from typing import Callable

import tkinter as tk

from checkers.game.game import Game


class CheckersUserInterface(tk.Tk):
    def __init__(self, resolution: tuple[int, int]) -> None:
        super().__init__()
        self.width, self.height = resolution

        self.geometry(f"{self.width}x{self.height}")
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
            (
                "YES I WANT TO START A NEW GAME AND LOSE!! (っ °Д °;)っ",
                self.open_new_game,
            ),
            ("GAME HISTORY", self.open_game_history),
            ("USER INFO", self.open_login),
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

    def open_new_game(self) -> None:
        print("open_game_history Not implemented")

    def open_game_history(self) -> None:
        print("open_game_history Not implemented")

    def open_login(self) -> None:
        print("open_login Not implemented")
