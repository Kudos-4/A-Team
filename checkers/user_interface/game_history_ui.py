import json
import tkinter as tk
from tkinter import ttk
from checkers.user_interface.screen import Screen
from checkers.auth.database import get_game_history


class GameHistoryScreen(Screen): # Displays a list of past games in a table format.


    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.configure(background="#f0f0f0") #color

    def run(self) -> None: #Initialize and display the game history screen.
        self._create_header()
        self._create_game_history_table()
        self._create_back_button()

    def _create_header(self) -> None: # Create the header section with title."""
        header_frame = tk.Frame(self, background="#2c3e50") #color
        header_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            header_frame,
            text="GAME HISTORY",
            font=("Comic Sans MS", 36, "bold"), # Idk if we keep this as comin sans or not xddd
            fg="white",
            bg="#2c3e50",
            pady=20,
        ).pack()

    def _create_game_history_table(self) -> None: #Create the main table displaying game history.
        # Includes Date, Time, Opponent, Result, Total Moves, and Move Record button
        # Container for the table
        table_frame = tk.Frame(self, background="#f0f0f0")
        table_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Create a canvas with scrollbar for scrolling capability
        canvas = tk.Canvas(table_frame, background="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=canvas.yview
        )
        # Single shared grid frame — headers and rows all go in here so columns align
        scrollable_frame = tk.Frame(canvas, background="#f0f0f0")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Fetch game history data (placeholder - will be implemented by another developer)
        game_history = self._fetch_game_history()

        if not game_history:
            # AC-4: No game history available message
            self._show_no_history_message(scrollable_frame)
        else:
            # AC-2: Display game history table with headers and rows in the same grid
            self._create_table_headers(scrollable_frame)
            self._populate_game_rows(scrollable_frame, game_history)

    def _fetch_game_history(self) -> list[dict]:
        """
        Placeholder method to fetch game history from database.
        """
       return get_game_history(self.user_id)


    def _show_no_history_message(self, parent: tk.Frame) -> None: # AC-4: Display message when no game history is available.

        message_frame = tk.Frame(parent, background="#f0f0f0")
        message_frame.pack(expand=True, fill="both", pady=100)

        tk.Label(
            message_frame,
            text="No game history available",
            font=("Arial", 28, "bold"),
            fg="#7f8c8d",
            bg="#f0f0f0",
        ).pack(pady=20)

        tk.Label(
            message_frame,
            text="Play some games to see your history here!",
            font=("Arial", 18),
            fg="#95a5a6",
            bg="#f0f0f0",
        ).pack()

    def _create_table_headers(self, parent: tk.Frame) -> None: #Create the table header row with column names.
        # Header labels go directly into the shared grid (row 0) alongside data rows
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
                font=("Arial", 14, "bold"),
                fg="white",
                bg="#34495e",
                padx=10,
                pady=10,
                anchor="w",
            ).grid(row=0, column=col_idx, sticky="ew", padx=(0, 2))

    def _populate_game_rows(
        self, parent: tk.Frame, game_history: list[dict]
    ) -> None: # Populate the table with game history rows.
        # AC-2: Each row shares the same grid as the headers, guaranteeing column alignment.

        for idx, game in enumerate(game_history):
            # Alternate row colors for better readability
            bg_color = "#ecf0f1" if idx % 2 == 0 else "#ffffff"
            grid_row = idx + 1  # Row 0 is the header

            # Date
            tk.Label(
                parent,
                text=game["date"],
                font=("Arial", 12),
                bg=bg_color,
                padx=10,
                pady=15,
                anchor="w",
            ).grid(row=grid_row, column=0, sticky="ew", padx=(0, 2))

            # Time
            tk.Label(
                parent,
                text=game["time"],
                font=("Arial", 12),
                bg=bg_color,
                padx=10,
                pady=15,
                anchor="w",
            ).grid(row=grid_row, column=1, sticky="ew", padx=(0, 2))

            # Opponent
            tk.Label(
                parent,
                text=game["opponent"],
                font=("Arial", 12, "bold"),
                bg=bg_color,
                padx=10,
                pady=15,
                anchor="w",
            ).grid(row=grid_row, column=2, sticky="ew", padx=(0, 2))

            # Result with color coding
            result_color = self._get_result_color(game["result"])
            tk.Label(
                parent,
                text=game["result"],
                font=("Arial", 12, "bold"),
                fg=result_color,
                bg=bg_color,
                padx=10,
                pady=15,
                anchor="w",
            ).grid(row=grid_row, column=3, sticky="ew", padx=(0, 2))

            # Total Moves
            tk.Label(
                parent,
                text=str(game["total_moves"]),
                font=("Arial", 12),
                bg=bg_color,
                padx=10,
                pady=15,
                anchor="w",
            ).grid(row=grid_row, column=4, sticky="ew", padx=(0, 2))

            # Move Record Button
            # AC-3: Button to open the move record file
            btn_frame = tk.Frame(parent, bg=bg_color, padx=10, pady=8)
            btn_frame.grid(row=grid_row, column=5, sticky="ew", padx=(0, 2))

            move_record_btn = tk.Button(
                btn_frame,
                text="Move Record",
                font=("Arial", 11, "bold"),
                bg="#3498db",
                fg="white",
                activebackground="#2980b9",
                activeforeground="white",
                relief="raised",
                borderwidth=2,
                cursor="hand2",
                command=lambda path=game["move_record_path"]: self._open_move_record(
                    path
                ),
            )
            move_record_btn.pack(anchor="w")

    def _get_result_color(self, result: str) -> str:
        """Return color based on game result."""
        color_map = {
            "Win": "#27ae60",  # Green
            "Loss": "#e74c3c",  # Red
            "Draw": "#f39c12",  # Orange
        }
        return color_map.get(result, "#000000")

    def _open_move_record(self, file_path: str) -> None:
        """
        AC-3: Open and display the move record file for a specific game.
        This will be implemented by another developer.

        Args:
            file_path: Path to the .txt file containing the move record
        """
        # TODO: Implement file reading and display in a new window or text viewer
        print(f"Opening move record file: {file_path}")
        # Placeholder: Show a message box indicating the feature is not yet implemented
        from tkinter import messagebox

        messagebox.showinfo(
            "Move Record",
            f"Move record file:\n{file_path}\n\n"
            "This feature will display the game moves when fully implemented.",
        )

    def _create_back_button(self) -> None:
        """Create a back button to return to the main menu."""
        button_frame = tk.Frame(self, background="#f0f0f0")
        button_frame.pack(pady=20)

        back_button = tk.Button(
            button_frame,
            text="← Back to Main Menu",
            font=("Arial", 18, "bold"),
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            activeforeground="white",
            relief="raised",
            borderwidth=3,
            cursor="hand2",
            padx=30,
            pady=15,
            command=self.destroy,
        )
        back_button.pack()
