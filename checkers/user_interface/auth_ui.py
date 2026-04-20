"""
auth_ui.py
Modernized Login and Register UI screens for the Checkers application.
Designed to work with CheckersUserInterface in ui.py.

Usage in ui.py:
    from checkers.user_interface.auth_ui import AuthUI
    auth = AuthUI(self, on_login_success=self._on_login_success)
    auth.show_login()
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable
from checkers.auth import auth_logic, auth


class AuthUI:
    """
    Handles Login and Register screens.
    Renders inside the main CheckersUserInterface (tk.Tk) window.
    """

    # Max failed login attempts before lockout
    MAX_ATTEMPTS = 5

    def __init__(
        self,
        root: tk.Tk,
        on_login_success: Callable[[str], None],
    ) -> None:
        """
        Args:
            root: The main tk.Tk window (CheckersUserInterface).
            on_login_success: Callback called with username when login succeeds.
        """
        self._root = root
        self._on_login_success = on_login_success
        self._failed_attempts = 0

        # Color system
        self.BG_APP = "#0f172a"
        self.BG_CARD = "#1e293b"
        self.BG_INPUT = "#334155"
        self.BG_TOPBAR = "#111827"
        self.FG_TEXT = "#f8fafc"
        self.FG_MUTED = "#94a3b8"
        self.COLOR_ACCENT = "#f43f5e"
        self.COLOR_ACCENT_HOVER = "#e11d48"
        self.COLOR_ERROR = "#ef4444"
        self.COLOR_SUCCESS = "#22c55e"

        # Typography
        self.FONT_TITLE = ("Arial", 26, "bold")
        self.FONT_SUBTITLE = ("Arial", 12)
        self.FONT_LABEL = ("Arial", 10, "bold")
        self.FONT_INPUT = ("Arial", 13)
        self.FONT_BUTTON = ("Arial", 12, "bold")
        self.FONT_SMALL = ("Arial", 10)

        # Login variables
        self._username_var = tk.StringVar()
        self._password_var = tk.StringVar()
        self._login_error_var = tk.StringVar()

        # Register variables
        self._reg_username_var = tk.StringVar()
        self._reg_email_var = tk.StringVar()
        self._reg_password_var = tk.StringVar()
        self._reg_confirm_var = tk.StringVar()
        self._reg_error_var = tk.StringVar()

    # ==========================================================================
    # Public methods shared with ui.py
    # ==========================================================================

    def show_login(self) -> None:
        """Render the login screen inside the root window."""
        self._clear()
        self._root.title("Checkers Pro - Login")
        self._root.configure(bg=self.BG_APP)

        self._add_top_bar()

        # Reset login-only fields
        self._password_var.set("")
        self._login_error_var.set("")

        container = tk.Frame(self._root, bg=self.BG_APP)
        container.place(relx=0.5, rely=0.52, anchor="center")

        card = tk.Frame(container, bg=self.BG_CARD, padx=44, pady=36)
        card.pack()

        tk.Label(
            card,
            text="CHECKERS PRO",
            font=self.FONT_TITLE,
            fg=self.COLOR_ACCENT,
            bg=self.BG_CARD,
        ).pack(pady=(0, 6))

        tk.Label(
            card,
            text="Welcome back! Please enter your details.",
            font=self.FONT_SUBTITLE,
            fg=self.FG_MUTED,
            bg=self.BG_CARD,
        ).pack(pady=(0, 18))

        tk.Label(
            card,
            textvariable=self._login_error_var,
            font=self.FONT_SMALL,
            fg=self.COLOR_ERROR,
            bg=self.BG_CARD,
            wraplength=360,
        ).pack(pady=(0, 8))

        self._build_input(card, "USERNAME", self._username_var, hidden=False)
        self._build_input(card, "PASSWORD", self._password_var, hidden=True)

        login_btn = tk.Button(
            card,
            text="SIGN IN",
            font=self.FONT_BUTTON,
            bg=self.COLOR_ACCENT,
            fg="white",
            activebackground=self.COLOR_ACCENT_HOVER,
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self._handle_login,
            padx=10,
            pady=10,
        )
        login_btn.pack(fill="x", pady=(22, 12))
        self._bind_hover(login_btn, self.COLOR_ACCENT, self.COLOR_ACCENT_HOVER)

        # Footer with register link
        footer = tk.Frame(card, bg=self.BG_CARD)
        footer.pack()

        tk.Label(
            footer,
            text="Don't have an account?",
            bg=self.BG_CARD,
            fg=self.FG_MUTED,
            font=self.FONT_SMALL,
        ).pack(side="left")

        reg_btn = tk.Button(
            footer,
            text="Sign up",
            font=("Arial", 10, "bold"),
            bg=self.BG_CARD,
            fg=self.COLOR_ACCENT,
            activebackground=self.BG_CARD,
            activeforeground=self.COLOR_ACCENT_HOVER,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.show_register,
        )
        reg_btn.pack(side="left", padx=6)

        # Enter key triggers login
        self._root.bind("<Return>", lambda _e: self._handle_login())

    def show_register(self) -> None:
        """Render the register screen inside the root window."""
        self._clear()
        self._root.title("Checkers Pro - Register")
        self._root.configure(bg=self.BG_APP)

        self._add_top_bar()
        self._reg_error_var.set("")
        self._reg_password_var.set("")
        self._reg_confirm_var.set("")

        container = tk.Frame(self._root, bg=self.BG_APP)
        container.place(relx=0.5, rely=0.53, anchor="center")

        card = tk.Frame(container, bg=self.BG_CARD, padx=44, pady=36)
        card.pack()

        tk.Label(
            card,
            text="CREATE ACCOUNT",
            font=("Arial", 24, "bold"),
            fg=self.COLOR_ACCENT,
            bg=self.BG_CARD,
        ).pack(pady=(0, 6))

        tk.Label(
            card,
            text="Join Checkers Pro in less than a minute.",
            font=self.FONT_SUBTITLE,
            fg=self.FG_MUTED,
            bg=self.BG_CARD,
        ).pack(pady=(0, 16))

        self._build_input(card, "USERNAME", self._reg_username_var, hidden=False)
        self._build_input(card, "EMAIL", self._reg_email_var, hidden=False)
        self._build_input(card, "PASSWORD", self._reg_password_var, hidden=True)
        self._build_input(card, "CONFIRM PASSWORD", self._reg_confirm_var, hidden=True)

        tk.Label(
            card,
            text=(
                "Password must include at least 8 characters with uppercase, "
                "lowercase, number, and special character."
            ),
            font=("Arial", 9),
            fg=self.FG_MUTED,
            bg=self.BG_CARD,
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(8, 4))

        tk.Label(
            card,
            textvariable=self._reg_error_var,
            font=self.FONT_SMALL,
            fg=self.COLOR_ERROR,
            bg=self.BG_CARD,
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(2, 10))

        btn_row = tk.Frame(card, bg=self.BG_CARD)
        btn_row.pack(fill="x", pady=(6, 0))

        register_btn = tk.Button(
            btn_row,
            text="REGISTER",
            font=self.FONT_BUTTON,
            bg=self.COLOR_ACCENT,
            fg="white",
            activebackground=self.COLOR_ACCENT_HOVER,
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self._handle_register,
            padx=10,
            pady=10,
        )
        register_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self._bind_hover(register_btn, self.COLOR_ACCENT, self.COLOR_ACCENT_HOVER)

        back_btn = tk.Button(
            btn_row,
            text="BACK TO LOGIN",
            font=("Arial", 11, "bold"),
            bg=self.BG_INPUT,
            fg=self.FG_TEXT,
            activebackground="#475569",
            activeforeground=self.FG_TEXT,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.show_login,
            padx=10,
            pady=10,
        )
        back_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))
        self._bind_hover(back_btn, self.BG_INPUT, "#475569")

        # Enter key triggers register
        self._root.bind("<Return>", lambda _e: self._handle_register())

    # ==========================================================================
    # Private: Login logic
    # ==========================================================================

    def _handle_login(self) -> None:
        """
        Validate fields and attempt login.
        - Empty fields -> error.
        - Wrong credentials -> error.
        - Lockout after MAX_ATTEMPTS failures.
        - Valid login -> on_login_success callback.
        """
        username = self._username_var.get().strip()
        password = self._password_var.get()

        if self._failed_attempts >= self.MAX_ATTEMPTS:
            self._login_error_var.set(
                "Too many failed attempts. Please restart and try again."
            )
            return

        field_error = auth_logic.validate_login_fields(username, password)
        if field_error:
            self._login_error_var.set(field_error)
            return

        login_result = auth.login_user(username, password)

        if login_result:
            self._failed_attempts = 0
            self._login_error_var.set("")
            # Support both possible return styles: bool or username
            logged_username = (
                login_result if isinstance(login_result, str) else username
            )
            self._on_login_success(logged_username)
        else:
            self._failed_attempts += 1
            remaining = self.MAX_ATTEMPTS - self._failed_attempts
            if remaining > 0:
                self._login_error_var.set(
                    f"Invalid credentials. {remaining} attempt(s) remaining."
                )
            else:
                self._login_error_var.set(
                    "Too many failed attempts. Please wait and try again."
                )

    # ==========================================================================
    # Private: Register logic
    # ==========================================================================

    def _handle_register(self) -> None:
        """
        Validate all fields and attempt registration.
        - Valid input -> account created.
        - Invalid input -> error message shown.
        - Success -> redirect to login.
        """
        username = self._reg_username_var.get().strip()
        email = self._reg_email_var.get().strip()
        password = self._reg_password_var.get()
        confirm = self._reg_confirm_var.get()

        error = auth_logic.validate_register_fields(username, email, password, confirm)
        if error:
            self._reg_error_var.set(error)
            if "password" in error.lower() or "match" in error.lower():
                self._clear_password_fields()
            return

        success, msg = auth.register_user(username, email, password)
        if success:
            messagebox.showinfo(
                "Account Created",
                f"Welcome, {username}!\nYour account has been created.\nPlease log in.",
            )
            self.show_login()
            self._username_var.set(username)
        else:
            self._reg_error_var.set(msg)
            self._clear_password_fields()

    def _clear_password_fields(self) -> None:
        """Clear register password fields only."""
        self._reg_password_var.set("")
        self._reg_confirm_var.set("")

    # ==========================================================================
    # Private: Shared UI helpers
    # ==========================================================================

    def _build_input(
        self,
        parent: tk.Widget,
        label: str,
        variable: tk.StringVar,
        hidden: bool = False,
    ) -> None:
        """Create a styled input row with label and entry."""
        wrap = tk.Frame(parent, bg=self.BG_CARD)
        wrap.pack(fill="x", pady=8)

        tk.Label(
            wrap,
            text=label,
            font=self.FONT_LABEL,
            fg=self.FG_MUTED,
            bg=self.BG_CARD,
        ).pack(anchor="w")

        entry = tk.Entry(
            wrap,
            textvariable=variable,
            show="*" if hidden else "",
            font=self.FONT_INPUT,
            bg=self.BG_INPUT,
            fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT,
            bd=0,
            relief="flat",
            highlightthickness=2,
            highlightbackground=self.BG_CARD,
            highlightcolor=self.COLOR_ACCENT,
        )
        entry.pack(fill="x", ipady=8, pady=(5, 0))

    def _bind_hover(self, button: tk.Button, normal_bg: str, hover_bg: str) -> None:
        """Add simple hover effect to a button."""
        button.bind("<Enter>", lambda _e: button.configure(bg=hover_bg))
        button.bind("<Leave>", lambda _e: button.configure(bg=normal_bg))

    def _add_top_bar(self) -> None:
        """Add a top bar showing current date/time from root._datetime_var."""
        top_bar = tk.Frame(self._root, bg=self.BG_TOPBAR)
        top_bar.pack(fill="x", padx=12, pady=(10, 0))

        tk.Label(
            top_bar,
            text="Checkers Pro",
            font=("Arial", 11, "bold"),
            fg=self.FG_MUTED,
            bg=self.BG_TOPBAR,
            padx=8,
            pady=6,
        ).pack(side="left")

        tk.Label(
            top_bar,
            textvariable=self._root._datetime_var,
            font=("Arial", 11),
            fg=self.FG_MUTED,
            bg=self.BG_TOPBAR,
            padx=8,
            pady=6,
        ).pack(side="right")

    def _clear(self) -> None:
        """Remove all widgets from the root window."""
        # Unbind Enter key when switching screens to avoid duplicate bindings
        self._root.unbind("<Return>")
        for widget in self._root.winfo_children():
            widget.destroy()
