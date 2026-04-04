from abc import ABC, abstractmethod
import tkinter as tk

class Screen(tk.Toplevel, ABC):
    def clear_screen(self) -> None:
        """Remove all widgets on screen"""
        for widget in tuple(self.children.values()):
            widget.destroy()

    @abstractmethod
    def run(self) -> None:
        """Acts as the injection point to run the new window"""
        pass