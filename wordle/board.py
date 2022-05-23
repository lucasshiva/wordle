from typing import List

from rich.columns import Columns
from rich.panel import Panel
from typing_extensions import Literal

from wordle import Wordle
from wordle.console import console
from wordle.locale import Locale
from wordle.modes import Mode


class Board:
    """A representation of a board.

    The board is comprised of two sections: a top section for the puzzles, a bottom section for the
    keyboard.
    """

    def __init__(
        self,
        mode: Mode,
        locale: Locale,
        debug: bool = False,
        alignment: Literal["left", "center", "right"] = "center",
    ):
        self.mode = mode
        self.locale = locale
        self.debug = debug
        self.alignment = alignment

        self.puzzles: List[Wordle] = []
        self._setup_puzzles()

    def _setup_puzzles(self) -> None:
        """Get the secret words and create the puzzles."""
        secrets = self.locale.get_secrets(amount=self.mode.puzzles_amount)
        for num, secret in enumerate(secrets, start=1):
            wordle = Wordle(id=num, secret=secret, mode=self.mode, locale=self.locale)
            self.puzzles.append(wordle)

    def draw(self) -> None:
        """Print an empty board on the screen."""
        console.clear()
        self._draw_puzzles()
        self._draw_keyboards()

    def guess(self, word: str) -> None:
        """Guess a word."""
        for puzzle in self.puzzles:
            puzzle.guess(word)

    def is_solved(self) -> bool:
        """Check if all the puzzles have been solved."""
        return all([p.is_solved for p in self.puzzles])

    def _draw_puzzles(self) -> None:
        """Print the puzzles on the screen."""
        panels: List[Panel] = []

        for puzzle in self.puzzles:
            panels.append(puzzle.get_panel(debug=self.debug))

        console.print(Columns(panels), justify=self.alignment)

    def _draw_keyboards(self) -> None:
        panels: List[Panel] = []
        for puzzle in self.puzzles:
            panels.append(puzzle.get_keyboard())

        console.print(Columns(panels), justify=self.alignment)
