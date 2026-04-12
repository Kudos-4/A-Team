from typing import Callable, Optional

import datetime
import tkinter as tk

from checkers.user_interface.screen import Screen
from checkers.user_interface.auth_ui import AuthUI
from checkers.user_interface.game_ui import GameScreen
from checkers.user_interface.game_history_ui import GameHistoryScreen
from checkers.auth.database import get_user_id

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
        self.current_user_id: Optional[int] = None
        
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
        self.current_user_id = get_user_id(username)
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
            text="Welcome to Checkers!!( •̀ ω •́ )y",
            font=("Calibri", 42),
            pady=10,
        )
        menu_title_label.pack()

        self.create_menu_buttons(
            ("NEW GAME", self.open_new_game),
            ("GAME HISTORY", self.open_game_history),
            ("LOG OUT", self.handle_logout),
            ("EXIT", self.destroy),
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
        **screen_kwargs,
    ) -> Screen:
        """Hides main menu and creates a new window to work off of."""
        self.withdraw()  # Hide function
        window = screen_type(**screen_kwargs)
        window.title(title)
        window.geometry(self.resolution_str)
        window.attributes("-fullscreen", enable_fullscreen)
        return window

    def open_game_history(self) -> None:
        """Opens the game history screen in a new window."""
        window_name = "Game History"
        history_window = self.switch_to_new_window(GameHistoryScreen, window_name, user_id=self.current_user_id)
        history_window.run()
        self.wait_window(history_window)
        self.wm_deiconify()

    def open_new_game(self) -> None:
        """Opens a new window instance of a checkers game."""
        game_window = self.switch_to_new_window(
            GameScreen,
            "🦅AMERICAN CHECKERS RAHHHHH🔫 GOD BLESS THIS COUNTRAAAY🛐 O(∩_∩)O" + " NEW YORK PIZZA" * 100,
            player1_username=self.current_user,
            user_id=self.current_user_id
        )
        game_window.run()
        self.wait_window(game_window)
        self.wm_deiconify()
