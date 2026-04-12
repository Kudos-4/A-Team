"""
auth.py
Handles user registration and login, including password hashing and database interaction.
connect auth_logic.py for pure validation logic, and database.py for SQLite access. 
UI will call these functions to perform auth operations.

required install: bcrypt (pip install bcrypt)
"""

import sqlite3
import bcrypt
from checkers.auth.database import get_connection

def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Register a new user. Returns (success, message).
    Paassword is hashed before storing. Handles unique username/email constraints.
    """
    username = username.lower()
    email = email.lower()
    pwd_hash = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    ).decode()

    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, email, pwd_hash) VALUES (?, ?, ?)",
            (username, email, pwd_hash)
        )
        conn.commit()
        conn.close()
        return True, ""
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username is already taken."
        return False, "Email address is already in use."
    finally:
        conn.close()

def login_user(username: str, password: str) -> "str | None":
    """Check credentials. Returns True if valid."""
    username = username.lower()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, pwd_hash FROM users WHERE username = ? OR email = ?",
        (username, username)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    if bcrypt.checkpw(password.encode(), row[1].encode()):
        return row[0]
    return None
