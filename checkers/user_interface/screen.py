from abc import ABC, abstractmethod
import tkinter as tk


class Screen(tk.Toplevel, ABC):
    """
    Base class for all secondary UI windows.

    This class centralizes common window behavior so each child screen
    (game screen, history screen, etc.) stays clean and consistent.
    """

    def __init__(self) -> None:
        super().__init__()

        # Keep a default background reference for easy reset in child classes.
        self.default_window_color = self.cget("bg")

        # Handle native window close event safely.
        self.protocol("WM_DELETE_WINDOW", self.close)

        # Optional keyboard shortcuts used by most screens.
        self.bind("<Escape>", lambda _: self.close())

    def clear_screen(self) -> None:
        """Remove all direct child widgets from the screen."""
        for widget in tuple(self.children.values()):
            widget.destroy()

    def close(self) -> None:
        """Destroy this screen window."""
        self.destroy()

    def set_theme(
        self,
        bg: str,
        title: str = "",
        fullscreen: bool | None = None,
    ) -> None:
        """
        Apply basic window-level styling in one place.

        Args:
            bg: Window background color.
            title: Optional window title.
            fullscreen: Optional fullscreen toggle.
        """
        if title:
            self.title(title)
        self.configure(bg=bg)
        if fullscreen is not None:
            self.attributes("-fullscreen", fullscreen)

    def center_window(self, width: int, height: int) -> None:
        """
        Center the window on the current display.

        Useful when fullscreen is disabled.
        """
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    @abstractmethod
    def run(self) -> None:
        """Injection point for rendering and starting the screen."""
        raise NotImplementedError
