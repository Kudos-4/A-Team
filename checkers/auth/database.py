import sqlite3
import os

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

    conn.commit()
    conn.close()