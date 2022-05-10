from dataclasses import dataclass, field

COLOR_IN_POSITION = "green"
COLOR_IN_WORD = "yellow"
COLOR_NOT_FOUND = "white"


@dataclass
class Letter:
    """A representation of a letter from a Wordle guess."""

    char: str
    in_word: bool = field(default=False, init=False)
    in_position: bool = field(default=False, init=False)

    @property
    def color(self) -> str:
        """Return the appropriate color for the letter."""
        if self.in_position:
            return COLOR_IN_POSITION
        elif self.in_word:
            return COLOR_IN_WORD
        else:
            return COLOR_NOT_FOUND
