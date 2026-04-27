from checkers.colors import ColorID
from dataclasses import dataclass


@dataclass(frozen=True)
class Player:
    username: str
    color: ColorID
