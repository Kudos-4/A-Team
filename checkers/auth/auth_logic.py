"""
auth_logic.py
Pure authentication logic — no Tkinter dependency.
This can be tested without a display and will later
connect to SQLite via auth.py.
"""

from typing import Optional

# ==========================================================================
#                       Password policy constants
# ==========================================================================
MIN_PASSWORD_LENGTH = 8
SPECIAL_CHARACTERS = "!@#$%^&*()_+-=[]{}|;':\",./<>?"


def validate_password_policy(password: str) -> Optional[str]:
    """
    Check password against policy requirements.
    Returns an error message string if invalid, or None if valid.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number."
    if not any(c in SPECIAL_CHARACTERS for c in password):
        return "Password must contain at least one special character."
    return None


def validate_email(email: str) -> bool:
    """Email validation: simple check for "@" and "." after "@". Not exhaustive."""
    return "@" in email and "." in email.split("@")[-1]


def validate_username(username: str) -> Optional[str]:
    """
    Validate username format.
    - Must be at least 3 characters
    - Must be alphanumeric (letters and numbers only)
    Returns error message string if invalid, or None if valid.
    """
    if len(username) < 3:
        return "Username must be at least 3 characters."
    if not username.isalnum():
        return "Username must contain only letters and numbers."
    return None


def validate_login_fields(username: str, password: str) -> Optional[str]:
    """Check that login fields are not empty. Returns error string or None."""
    if not username.strip() or not password:
        return "Please fill in all required fields."
    return None


def validate_register_fields(
    username: str, email: str, password: str, confirm: str
) -> Optional[str]:
    """
    Validate all registration fields in order.
    Returns first error found, or None if all valid.
    """
    if not username or not email or not password or not confirm:
        return "Please fill in all required fields."
    if password != confirm:
        return "Passwords do not match."
    username_error = validate_username(username)
    if username_error:
        return username_error
    if not validate_email(email):
        return "Invalid email format (e.g. user@example.com)."
    password_error = validate_password_policy(password)
    if password_error:
        return password_error
    return None
