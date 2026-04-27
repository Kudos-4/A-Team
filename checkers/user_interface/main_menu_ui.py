from typing import Callable, Optional
from tkinter import messagebox
import tkinter as tk
import datetime

from checkers.colors import Color
from checkers.user_interface import Screen, AuthUI
from checkers.auth import database


class MainMenuUI(tk.Tk):
    def __init__(self, resolution: tuple[int, int]) -> None:
        super().__init__()
        self.width, self.height = resolution
        self.resolution_str = f"{self.width}x{self.height}"
        self.geometry(self.resolution_str)
        self.attributes("-fullscreen", True)
        self.title("Checkers Pro")

        self.configure(bg=Color.BG_APP)

        # Track logged-in user
        self.current_user: Optional[str] = None
        self.current_user_id: Optional[int] = None

        # Shared live clock
        self._datetime_var = tk.StringVar()
        self.tick_datetime()

        # Authentication UI
        self._auth = AuthUI(self, on_login_success=self.login_success)
        self._auth.show_login()

    def login_success(self, username: str) -> None:
        """
        Called by AuthUI when login succeeds.
        Stores user session and opens the main menu.
        """
        self.current_user = username
        self.current_user_id = database.get_user_id(username)
        self.main_menu()

    def main_menu(self) -> None:
        """Render the main menu screen."""
        self.title("Checkers Pro - Main Menu")
        self._clear_root()
        self.configure(bg=Color.BG_APP)

        # Top bar
        top_bar = tk.Frame(self, bg=Color.BG_TOPBAR)
        top_bar.pack(fill="x", padx=16, pady=(10, 0))

        tk.Label(
            top_bar,
            textvariable=self._datetime_var,
            font=("Arial", 14),
            fg=Color.FG_MUTED,
            bg=Color.BG_TOPBAR,
            padx=8,
            pady=8,
            anchor="w",
        ).pack(side="left")

        tk.Label(
            top_bar,
            text=f"Player: {self.current_user or 'Unknown'}",
            font=("Arial", 14, "bold"),
            fg=Color.FG_TEXT,
            bg=Color.BG_TOPBAR,
            padx=8,
            pady=8,
            anchor="e",
        ).pack(side="right")

        # Center card
        container = tk.Frame(self, bg=Color.BG_APP)
        container.place(relx=0.5, rely=0.53, anchor="center")

        card = tk.Frame(container, bg=Color.BG_CARD, padx=42, pady=36)
        card.pack()

        tk.Label(
            card,
            text="CHECKERS PRO",
            font=("Arial", 34, "bold"),
            fg=Color.FG_ACCENT,
            bg=Color.BG_CARD,
        ).pack(pady=(0, 6))

        tk.Label(
            card,
            text="Choose what you want to do",
            font=("Arial", 12),
            fg=Color.FG_MUTED,
            bg=Color.BG_CARD,
        ).pack(pady=(0, 26))

        self._create_menu_button(card, "NEW GAME", self.open_new_game).pack(
            fill="x", pady=8
        )
        self._create_menu_button(card, "GAME HISTORY", self.open_game_history).pack(
            fill="x", pady=8
        )
        self._create_menu_button(card, "LOG OUT", self.handle_logout).pack(
            fill="x", pady=8
        )
        self._create_menu_button(
            card,
            "EXIT",
            self.destroy,
            bg=Color.BG_DANGER,
            hover_bg=Color.BG_DANGER_HOVER,
        ).pack(fill="x", pady=(8, 0))

        # Keyboard shortcut
        self.bind("<Escape>", lambda _: self.destroy())

    def handle_logout(self) -> None:
        """Clear session and return to login screen."""
        self.current_user = None
        self.current_user_id = None
        self._auth.show_login()

    def tick_datetime(self) -> None:
        """Update the shared clock variable every second."""
        now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self._datetime_var.set(now)
        self.after(1000, self.tick_datetime)

    def _create_menu_button(
        self,
        parent: tk.Widget,
        text: str,
        command: Callable,
        bg: Optional[str] = None,
        hover_bg: Optional[str] = None,
    ) -> tk.Button:
        """Create a themed menu button with hover effect."""
        base_bg = bg or Color.BG_BUTTON
        over_bg = hover_bg or Color.BG_BUTTON_HOVER

        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 16, "bold"),
            bg=base_bg,
            fg=Color.FG_TEXT,
            activebackground=over_bg,
            activeforeground=Color.FG_TEXT,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=12,
            command=command,
        )

        button.bind("<Enter>", lambda _: button.configure(bg=over_bg))
        button.bind("<Leave>", lambda _: button.configure(bg=base_bg))
        return button

    def switch_to_new_window(
        self,
        screen_type: type[Screen],
        title: str = "",
        enable_fullscreen: bool = True,
        **screen_kwargs,
    ) -> Screen:
        """Hide main menu and open a child screen window."""
        self.withdraw()
        window = screen_type(**screen_kwargs)
        window.title(title)
        window.geometry(self.resolution_str)
        window.attributes("-fullscreen", enable_fullscreen)
        return window

    def open_game_history(self) -> None:
        """Open the game history screen."""
        if self.current_user_id is None:
            messagebox.showerror(
                "Error", "User session is invalid. Please log in again."
            )
            self.handle_logout()
            return

        # Lazy import to avoid circular import at module load time
        from checkers.user_interface.game_history_ui import GameHistoryScreen

        history_window = self.switch_to_new_window(
            GameHistoryScreen,
            title="Game History",
            user_id=self.current_user_id,
        )
        history_window.run()
        self.wait_window(history_window)
        self.wm_deiconify()
        self.main_menu()

    def open_new_game(self) -> None:
        """Open a new game screen."""
        if self.current_user_id is None or self.current_user is None:
            messagebox.showerror(
                "Error", "User session is invalid. Please log in again."
            )
            self.handle_logout()
            return

        # Lazy import to avoid circular import at module load time
        from checkers.user_interface.game_ui import GameScreen

        game_window = self.switch_to_new_window(
            GameScreen,
            title="Checkers Pro - New Game",
            player1_username=self.current_user,
            user_id=self.current_user_id,
        )
        game_window.run()
        self.wait_window(game_window)
        self.wm_deiconify()
        self.main_menu()

    def _clear_root(self) -> None:
        """Remove all widgets from the root window."""
        self.unbind("<Escape>")
        for widget in self.winfo_children():
            widget.destroy()
