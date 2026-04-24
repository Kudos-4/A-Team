import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Any

from checkers.auth import database
from checkers.user_interface import Screen
from checkers.user_interface.replay_ui import ReplayScreen


class GameHistoryScreen(Screen):
    """Displays the user's past games in a styled, scrollable table."""

    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id

        # Theme palette
        self.BG_APP = "#0f172a"
        self.BG_TOPBAR = "#111827"
        self.BG_CARD = "#1e293b"
        self.BG_HEADER = "#334155"
        self.BG_ROW_A = "#243447"
        self.BG_ROW_B = "#1f2f42"
        self.BG_BUTTON = "#334155"
        self.BG_BUTTON_HOVER = "#475569"
        self.FG_TEXT = "#f8fafc"
        self.FG_MUTED = "#94a3b8"
        self.FG_ACCENT = "#f43f5e"

        self.configure(background=self.BG_APP)

    def run(self) -> None:
        """Initialize and render the game history screen."""
        self.clear_screen()
        self.configure(background=self.BG_APP)

        self._create_top_bar()
        self._create_header()
        self._create_game_history_table()
        self._create_back_button()

    def _create_top_bar(self) -> None:
        """Create a slim top bar for visual consistency."""
        top_bar = tk.Frame(self, bg=self.BG_TOPBAR)
        top_bar.pack(fill="x", padx=16, pady=(10, 0))

        tk.Label(
            top_bar,
            text="Checkers Pro",
            font=("Arial", 11, "bold"),
            fg=self.FG_MUTED,
            bg=self.BG_TOPBAR,
            padx=8,
            pady=8,
        ).pack(side="left")

    def _create_header(self) -> None:
        """Create the title section."""
        header_frame = tk.Frame(self, background=self.BG_APP)
        header_frame.pack(fill="x", pady=(18, 6))

        tk.Label(
            header_frame,
            text="GAME HISTORY",
            font=("Arial", 34, "bold"),
            fg=self.FG_ACCENT,
            bg=self.BG_APP,
        ).pack()

        tk.Label(
            header_frame,
            text="Review your recent matches and results",
            font=("Arial", 12),
            fg=self.FG_MUTED,
            bg=self.BG_APP,
        ).pack(pady=(6, 0))

    def _create_game_history_table(self) -> None:
        """Create a scrollable table for game history."""
        card = tk.Frame(self, bg=self.BG_CARD, padx=16, pady=16)
        card.pack(fill="both", expand=True, padx=28, pady=16)

        table_frame = tk.Frame(card, background=self.BG_CARD)
        table_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            table_frame,
            background=self.BG_CARD,
            highlightthickness=0,
            bd=0,
        )
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)

        scrollable_frame = tk.Frame(canvas, background=self.BG_CARD)

        # Keep canvas scroll region in sync with content size
        scrollable_frame.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mouse wheel scrolling while cursor is over table
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        game_history = self._fetch_game_history()

        if not game_history:
            self._show_no_history_message(scrollable_frame)
            return

        self._create_table_headers(scrollable_frame)
        self._populate_game_rows(scrollable_frame, game_history)

        # Improve column stretch behavior
        for col in range(6):
            scrollable_frame.grid_columnconfigure(col, weight=1)

    def _fetch_game_history(self) -> list[dict[str, Any]]:
        """Fetch game history records from database layer."""
        try:
            data = database.get_game_history(self.user_id)
            return data if isinstance(data, list) else []
        except Exception:
            # Fail-safe path to keep UI responsive even if DB call fails
            return []

    def _show_no_history_message(self, parent: tk.Frame) -> None:
        """Show a friendly empty-state message when no history exists."""
        message_frame = tk.Frame(parent, background=self.BG_CARD)
        message_frame.pack(expand=True, fill="both", pady=90)

        tk.Label(
            message_frame,
            text="No game history available",
            font=("Arial", 24, "bold"),
            fg=self.FG_TEXT,
            bg=self.BG_CARD,
        ).pack(pady=(0, 10))

        tk.Label(
            message_frame,
            text="Play some games and your records will appear here.",
            font=("Arial", 14),
            fg=self.FG_MUTED,
            bg=self.BG_CARD,
        ).pack()

    def _create_table_headers(self, parent: tk.Frame) -> None:
        """Create the table header row."""
        columns = [
            ("Date", 0),
            ("Time", 1),
            ("Opponent", 2),
            ("Result", 3),
            ("Total Moves", 4),
            ("Move Record", 5),
        ]

        for col_text, col_idx in columns:
            tk.Label(
                parent,
                text=col_text,
                font=("Arial", 13, "bold"),
                fg=self.FG_TEXT,
                bg=self.BG_HEADER,
                padx=10,
                pady=10,
                anchor="w",
            ).grid(row=0, column=col_idx, sticky="ew", padx=(0, 2), pady=(0, 2))

    def _populate_game_rows(
        self, parent: tk.Frame, game_history: list[dict[str, Any]]
    ) -> None:
        """Populate rows using normalized game data."""
        for idx, raw_game in enumerate(game_history):
            game = self._normalize_game_record(raw_game)

            bg_color = self.BG_ROW_A if idx % 2 == 0 else self.BG_ROW_B
            grid_row = idx + 1

            tk.Label(
                parent,
                text=game["date"],
                font=("Arial", 11),
                fg=self.FG_TEXT,
                bg=bg_color,
                padx=10,
                pady=12,
                anchor="w",
            ).grid(row=grid_row, column=0, sticky="ew", padx=(0, 2), pady=(0, 2))

            tk.Label(
                parent,
                text=game["time"],
                font=("Arial", 11),
                fg=self.FG_TEXT,
                bg=bg_color,
                padx=10,
                pady=12,
                anchor="w",
            ).grid(row=grid_row, column=1, sticky="ew", padx=(0, 2), pady=(0, 2))

            tk.Label(
                parent,
                text=game["opponent"],
                font=("Arial", 11, "bold"),
                fg=self.FG_TEXT,
                bg=bg_color,
                padx=10,
                pady=12,
                anchor="w",
            ).grid(row=grid_row, column=2, sticky="ew", padx=(0, 2), pady=(0, 2))

            tk.Label(
                parent,
                text=game["result"],
                font=("Arial", 11, "bold"),
                fg=self._get_result_color(game["result"]),
                bg=bg_color,
                padx=10,
                pady=12,
                anchor="w",
            ).grid(row=grid_row, column=3, sticky="ew", padx=(0, 2), pady=(0, 2))

            tk.Label(
                parent,
                text=str(game["total_moves"]),
                font=("Arial", 11),
                fg=self.FG_TEXT,
                bg=bg_color,
                padx=10,
                pady=12,
                anchor="w",
            ).grid(row=grid_row, column=4, sticky="ew", padx=(0, 2), pady=(0, 2))

            btn_frame = tk.Frame(parent, bg=bg_color, padx=10, pady=6)
            btn_frame.grid(
                row=grid_row, column=5, sticky="ew", padx=(0, 2), pady=(0, 2)
            )

            move_record_btn = tk.Button(
                btn_frame,
                text="View Moves",
                font=("Arial", 10, "bold"),
                bg="#3b82f6",
                fg="white",
                activebackground="#2563eb",
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda moves=game["moves"], opp=game["opponent"], res=game["result"], dt=game["date"]: (
                    self._open_move_record(moves, opp, res, dt)
                ),
                padx=10,
                pady=6,
            )
            move_record_btn.pack(anchor="w")

    def _normalize_game_record(self, game: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize possible DB/file formats into one consistent structure.
        Supports:
        - date/time
        - Date/Time
        - played_at (YYYY-mm-dd HH:MM:SS)
        """
        date = str(game.get("date", "") or game.get("Date", ""))
        time = str(game.get("time", "") or game.get("Time", ""))

        played_at = game.get("played_at")
        if (not date or not time) and played_at:
            try:
                dt = datetime.strptime(str(played_at), "%Y-%m-%d %H:%M:%S")
                date = date or dt.strftime("%Y-%m-%d")
                time = time or dt.strftime("%H:%M:%S")
            except ValueError:
                pass

        opponent = str(game.get("opponent", "") or game.get("Opponent", "Unknown"))
        result = str(game.get("result", "") or game.get("Result", "Unknown"))
        total_moves = game.get("total_moves", game.get("Total Moves", 0))
        moves = game.get("moves", game.get("Move Record", []))
        move_record_path = str(game.get("move_record_path", ""))

        return {
            "date": date or "-",
            "time": time or "-",
            "opponent": opponent,
            "result": result,
            "total_moves": total_moves if total_moves is not None else 0,
            "moves": moves if isinstance(moves, list) else [],
            "move_record_path": move_record_path,
        }

    def _get_result_color(self, result: str) -> str:
        """Return text color based on result."""
        normalized = result.lower().strip()
        if normalized == "win":
            return "#22c55e"
        if normalized == "loss":
            return "#ef4444"
        if normalized == "draw":
            return "#f59e0b"
        return self.FG_TEXT

    def _open_move_record(self, moves: list[Any], opponent: str, result: str, date: str) -> None:
        """Open the replay visualization for a past game."""
        if not moves:
            messagebox.showinfo("Move Record", "No move record data is available for this game.")
            return
        ReplayScreen(self, moves, opponent, result, date)

    def _create_back_button(self) -> None:
        """Create a themed back button."""
        button_frame = tk.Frame(self, background=self.BG_APP)
        button_frame.pack(pady=(0, 22))

        back_button = tk.Button(
            button_frame,
            text="← Back to Main Menu",
            font=("Arial", 14, "bold"),
            bg=self.BG_BUTTON,
            fg=self.FG_TEXT,
            activebackground=self.BG_BUTTON_HOVER,
            activeforeground=self.FG_TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=26,
            pady=12,
            command=self.destroy,
        )
        back_button.pack()

        back_button.bind(
            "<Enter>", lambda _e: back_button.configure(bg=self.BG_BUTTON_HOVER)
        )
        back_button.bind("<Leave>", lambda _e: back_button.configure(bg=self.BG_BUTTON))
