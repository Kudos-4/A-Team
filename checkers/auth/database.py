import sqlite3
import os
from typing import Optional
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "../../checkers.db")

def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def init_db() -> None:
    """
    Create all tables if they don't exist.
    Call in main.py before starting UI to ensure database is ready.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            pwd_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Games table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            opponent_name TEXT NOT NULL DEFAULT 'Guest',
            result TEXT NOT NULL,
            total_moves INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            record_file TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # fetch userid from current username for future use
    def get_user_id(username: str) -> Optional[int]:
        """Return the user's id for the given username, or None if not found."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    # link with game table to save and fetch game history
    def save_game(
        user_id: int,
        opponent_name: str,
        result: str,
        total_moves: int,
        moves: list[str],
    ) -> None:
        """Insert a completed game record into the games table."""
        conn = get_connection()
        conn.execute(
            "INSERT INTO games (user_id, opponent_name, result, total_moves, record_file)"
            " VALUES (?, ?, ?, ?, ?)",
            (user_id, opponent_name, result, total_moves, json.dumps(moves)),
        )
        conn.commit()
        conn.close()
    

    conn.commit()
    conn.close()
