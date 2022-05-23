from dataclasses import dataclass, field

from unidecode import unidecode


@dataclass
class Letter:
    """A representation of a letter from a Wordle guess."""

    _char: str
    in_word: bool = field(default=False, init=False)
    in_position: bool = field(default=False, init=False)

    @property
    def char(self) -> str:
        return self._char.upper()

    @property
    def unaccented_char(self) -> str:
        return unidecode(self.char)

    @property
    def color(self) -> str:
        """Return the appropriate color for the letter."""
        if self.in_position:
            return "green"
        elif self.in_word:
            return "yellow"
        else:
            return "white"

    @property
    def rich_color(self) -> str:
        """Return a valid `rich` colored string for the letter.

        Examples:
            >>> letter = Letter("a", in_word=True).rich_color
            '[bold yellow]a[/]'
        """
        return f"[bold {self.color}]{self.char}[/]"
