# A-Team Checkers

A full-featured American checkers game implemented in Python 3.12, built as a collaborative software-engineering project. Includes user authentication, a persistent game-history database, a graphical interface, and a pytest test suite.

## Features

- **Full American checkers rules** — standard movement, mandatory captures, king promotion
- **User authentication** — register/login system with a SQLite-backed user database
- **Game history** — all completed games stored in `checkers.db` and viewable through a history UI
- **Graphical interface** — built with Pygame; separate screens for auth, gameplay, and history
- **Test suite** — pytest tests covering game logic, piece behavior, board state, and auth

## Getting Started

### Requirements

```bash
pip install pygame pytest
```

### Run the game

```bash
python main.py
```

### Run tests

From the project root:

```bash
pytest
```

Per pytest conventions, all test files are in `tests/` and start with `test_*.py`. All test functions start with `test_`.

## Project Structure

```
A-Team-repo/
├── main.py                        # Entry point / dependency injection
├── checkers.db                    # SQLite database (auto-created on first run)
├── checkers/
│   ├── auth/
│   │   ├── auth.py                # Authentication facade
│   │   ├── auth_logic.py          # Login/register business logic
│   │   └── database.py            # SQLite connection and queries
│   ├── constants/
│   │   └── colors.py              # Color constants for the UI
│   ├── game/
│   │   ├── board.py               # Board representation and move generation
│   │   ├── game.py                # Game state and turn management
│   │   └── pieces.py              # Piece logic (movement, king promotion)
│   └── user_interface/
│       ├── auth_ui.py             # Login/registration screen
│       ├── game_history_ui.py     # Game history viewer
│       ├── game_ui.py             # Main gameplay screen
│       ├── screen.py              # Screen/window management
│       └── ui.py                  # UI entry point / screen router
└── tests/
    └── test_*.py                  # pytest test files
```

> **Note:** All files inside `checkers/` are treated as packages. Run them with `python -m checkers.game.pieces` (dot notation, no `.py`) rather than directly.

## Architecture

The project is separated into three independent layers:

| Layer | Responsibility |
|-------|---------------|
| `auth/` | User registration, login, and session management |
| `game/` | Pure game logic — board state, legal moves, win detection |
| `user_interface/` | Pygame rendering and user input; calls into game and auth layers |

This separation makes the game logic independently testable without a display.

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.12 | Core language |
| Pygame | Graphical interface |
| SQLite3 | Persistent user and game-history storage |
| pytest | Automated testing |

## Authors

A-Team — Collaborative project  
Jason Ramirez Medina (contributor) — Computer Science / Finance / Mathematics  
University of South Carolina Upstate
