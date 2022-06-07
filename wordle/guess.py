from dataclasses import dataclass
from typing import List

from wordle.letter import Letter


@dataclass
class Guess:
    """A representation of a guess."""

    word: str
    letters: List[Letter]

    def as_colored_string(self) -> str:
        """Return a valid `rich` string for the current guess."""
        colored = ""
        for letter in self.letters:
            colored += f" {letter.rich_color()} "
        return colored
