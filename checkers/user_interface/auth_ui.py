"""
auth_ui.py
Login and Register UI screens for the Checkers application.
Designed to work with CheckersUserInterface in ui.py.

Usage in ui.py:
    from checkers.user_interface.auth_ui import AuthUI
    auth = AuthUI(self, on_login_success=self._on_login_success)
    auth.show_login()
"""

import tkinter as tk
from typing import Callable
from tkinter import messagebox
from checkers.auth.auth import register_user, login_user
from checkers.auth.auth_logic import validate_login_fields, validate_register_fields


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
            root:             The main tk.Tk window (CheckersUserInterface).
            on_login_success: Callback called with username when login succeeds.
                              Use this to switch to the main menu in ui.py.
        """
        self._root = root
        self._on_login_success = on_login_success
        self._failed_attempts: int = 0

        # StringVars — created fresh on each screen render
        self._username_var: tk.StringVar
        self._password_var: tk.StringVar
        self._login_error_var: tk.StringVar
        self._reg_username_var: tk.StringVar
        self._reg_email_var: tk.StringVar
        self._reg_password_var: tk.StringVar
        self._reg_confirm_var: tk.StringVar
        self._reg_error_var: tk.StringVar
        self._datetime_var: tk.StringVar

    # ==========================================================================
    #                           Public methods: shared with ui.py
    # ==========================================================================

    def show_login(self) -> None:
        """
        Render the login screen inside the root window.
        Login form shown when game launches.
        Login form shown with empty fields after logout.
        """
        self._clear()
        self._root.title("Login")

        self._username_var = tk.StringVar()
        self._password_var = tk.StringVar()
        self._login_error_var = tk.StringVar()
        self._failed_attempts = 0

        # Add date/time top bar (shared with register screen)
        self._add_top_bar()

        container = tk.Frame(self._root)
        container.place(relx=0.5, rely=0.55, anchor="center")

        # Title and welcome message
        tk.Label(
            container,
            text="Welcome to Checker HELL!!( •̀ ω •́ )y",
            font=("Comic Sans MS", 36),
        ).pack(pady=(0, 10))

        # Login form title
        tk.Label(
            container,
            text="Login",
            font=("Arial", 28, "bold"),
        ).pack(pady=(0, 20))

        # Login Form
        form = tk.Frame(container)
        form.pack()

        tk.Label(form, text="Username or Email:", font=("Arial", 18)).grid(
            row=0, column=0, sticky="e", padx=10, pady=10
        )
        tk.Entry(
            form, textvariable=self._username_var, font=("Arial", 18), width=28
        ).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(form, text="Password:", font=("Arial", 18)).grid(
            row=1, column=0, sticky="e", padx=10, pady=10
        )
        tk.Entry(
            form,
            textvariable=self._password_var,
            font=("Arial", 18),
            width=28,
            show="*",
        ).grid(row=1, column=1, padx=10, pady=10)

        # Error label
        tk.Label(
            container,
            textvariable=self._login_error_var,
            font=("Arial", 14),
            fg="red",
        ).pack(pady=(8, 0))

        # Buttons
        btn_frame = tk.Frame(container)
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Login",
            font=("Arial", 22),
            width=12,
            command=self._handle_login,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame,
            text="Register",
            font=("Arial", 22),
            width=12,
            command=self.show_register,
        ).grid(row=0, column=1, padx=10)

    def show_register(self) -> None:
        """
        Render the register screen inside the root window.
        Register form opens from login with empty fields.
        """
        self._clear()
        self._root.title("Register")

        self._reg_username_var = tk.StringVar()
        self._reg_email_var = tk.StringVar()
        self._reg_password_var = tk.StringVar()
        self._reg_confirm_var = tk.StringVar()
        self._reg_error_var = tk.StringVar()

        # Top bar: date and time
        self._add_top_bar()

        # Centered container 
        container = tk.Frame(self._root)
        container.place(relx=0.5, rely=0.55, anchor="center")

        tk.Label(
            container,
            text="Create Account",
            font=("Arial", 28, "bold"),
        ).pack(pady=(0, 20))

        # Register form
        form = tk.Frame(container)
        form.pack()

        fields = [
            ("Username:", self._reg_username_var, False),
            ("Email Address:", self._reg_email_var, False),
            ("Password:", self._reg_password_var, True),
            ("Confirm Password:", self._reg_confirm_var, True),
        ]
        for i, (label, var, hidden) in enumerate(fields):
            tk.Label(form, text=label, font=("Arial", 16)).grid(
                row=i, column=0, sticky="e", padx=10, pady=8
            )
            tk.Entry(
                form,
                textvariable=var,
                font=("Arial", 16),
                width=26,
                show="*" if hidden else "",
            ).grid(row=i, column=1, padx=10, pady=8)

        # Password requirements
        tk.Label(
            container,
            text=(
                "Password: min 8 characters, uppercase, lowercase, "
                "number, special character"
            ),
            font=("Arial", 12),
            fg="gray",
            wraplength=500,
        ).pack(pady=(10, 0))

        # Error label
        tk.Label(
            container,
            textvariable=self._reg_error_var,
            font=("Arial", 13),
            fg="red",
            wraplength=500,
        ).pack(pady=(5, 0))

        # Buttons
        btn_frame = tk.Frame(container)
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Register",
            font=("Arial", 18),
            width=12,
            command=self._handle_register,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame,
            text="Back to Login",
            font=("Arial", 18),
            width=14,
            command=self.show_login,
        ).grid(row=0, column=1, padx=10)

    # ==========================================================================
    #                           Private: Login logic 
    # ==========================================================================

    def _handle_login(self) -> None:
        """
        Validate fields and attempt login.
        - Empty fields -> error.
        - Wrong credentials -> error.
        - Lockout after MAX_ATTEMPTS failures -> need to restart.
        - Valid login -> on_login_success callback.
        """
        username = self._username_var.get().strip()
        password = self._password_var.get()

        # Lockout check
        if self._failed_attempts >= self.MAX_ATTEMPTS:
            self._login_error_var.set(
                "Too many failed attempts. Please restart and try again."
            )
            return

        # Empty field check
        field_error = validate_login_fields(username, password)
        if field_error:
            self._login_error_var.set(field_error)
            return

        # Credential check
        success = login_user(username, password)

        if success:
            self._failed_attempts = 0 # reset on successful login
            self._login_error_var.set("")
            self._on_login_success(username)  # hand control back to ui.py
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
    #                           Private: Register logic
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

        error = validate_register_fields(username, email, password, confirm)
        if error:
            self._reg_error_var.set(error)
            if "password" in error.lower() or "match" in error.lower():
                self._clear_password_fields()
            return

        success, msg = register_user(username, email, password)

        if success:
            # Success message -> redirect to login
            messagebox.showinfo(
                "Account Created",
                f"Welcome, {username}!\nYour account has been created.\nPlease log in.",
            )
            self.show_login()
            self._username_var.set(username)  # pre-fill username on login form
        else:
            # Duplicate username or email -> show error and clear password fields
            self._reg_error_var.set(msg)
            self._clear_password_fields()

    def _clear_password_fields(self) -> None:
        """Clear password fields only — keep username and email."""
        self._reg_password_var.set("")
        self._reg_confirm_var.set("")

    # ==========================================================================
    #                           Private: Shared helpers
    # ==========================================================================

    def _clear(self) -> None:
        """Remove all widgets from the root window."""
        for widget in self._root.winfo_children():
            widget.destroy()

    def _add_top_bar(self) -> None:
        """Add a top bar showing the current date and time on every screen."""
        top_bar = tk.Frame(self._root)
        top_bar.pack(fill="x", padx=16, pady=(8, 0))

        tk.Label(
            top_bar,
            textvariable=self._root._datetime_var,
            font=("Arial", 16),
            anchor="w",
        ).pack(side="left")
