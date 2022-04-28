from dataclasses import dataclass, field
from typing import List

from wordle.modes import Mode

Guess = List["Letter"]


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
            return "green"
        elif self.in_word:
            return "yellow"
        else:
            return "gray"


class Wordle:

    WORD_LENGTH = 5

    def __init__(self, secret: str, mode: Mode = Mode.from_name("solo")) -> None:
        self.secret = secret.upper()  # Ensure the secret is in uppercase.
        self.mode = mode

        # Keep track of all the guesses.
        self.guesses: List[Guess] = []

        # Same as above, but leave guesses as strings.
        self.attempts: List[str] = []

    def _compare(self, word: str) -> Guess:
        """Compare a word with the secret word."""
        letters = [Letter(char) for char in word]
        remaining_secret = list(self.secret)

        # Get the greens first.
        for index in range(self.WORD_LENGTH):
            letter = letters[index]
            if letter.char == remaining_secret[index]:
                letter.in_position = True

                # We can't use .pop() here, as that would change the list's size.
                remaining_secret[index] = "*"

        # Now we look for yellows.
        for index in range(self.WORD_LENGTH):
            letter = letters[index]
            if letter.char in remaining_secret:
                letter.in_word = True
                remaining_secret.remove(letter.char)

        return letters

    @property
    def is_solved(self) -> bool:
        """Check whether the last guess was correct."""
        return (len(self.attempts) > 0) and (self.attempts[-1] == self.secret)

    @property
    def remaining_attempts(self) -> int:
        """Return the amount of remaining attempts."""
        return self.mode.max_guesses - len(self.attempts)

    def guess(self, word: str) -> Guess:
        """Guess a word.

        Args:
            word: A string to guess.

        Returns:
            An instance of `Guess`.

        Raises:
            ValueError: If the word is not 5 characters long.

        Examples:
            >>> guess = wordle.guess(word)
            >>> for letter in guess:
            >>>     print(letter.in_word)
            <True>
            <False>
            ...
        """
        # Do nothing if we have already solved this wordle.
        # This is for duo and quad modes.
        if self.is_solved:
            return []

        # NOTE: We could use an original exception for this, but ValueError works just fine.
        if len(word) != self.WORD_LENGTH:
            raise ValueError(f"Guesses must have exactly {self.WORD_LENGTH} characters.")

        letters = self._compare(word)
        self.attempts.append(word)
        self.guesses.append(letters)
        return letters
