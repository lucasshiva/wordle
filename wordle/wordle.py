from typing import List

from wordle.exceptions import GuessLengthError, GuessNotFoundError
from wordle.letter import Letter
from wordle.locale import Locale
from wordle.modes import Mode

Guess = List["Letter"]
WORD_LENGTH = 5


class Wordle:
    def __init__(self, secret: str, mode: Mode, locale: Locale) -> None:
        self.secret = secret.upper()  # Ensure the secret is in uppercase.
        self.mode = mode
        self.locale = locale

        # Keep track of all the guesses.
        self.guesses: List[Guess] = []

        # Same as above, but leave guesses as strings.
        self.attempts: List[str] = []

    def _compare(self, word: str) -> Guess:
        """Compare a word with the secret word."""
        letters = [Letter(char) for char in word]
        remaining_secret = list(self.secret)

        # Get the greens first.
        for index in range(WORD_LENGTH):
            letter = letters[index]
            if letter.char == remaining_secret[index]:
                letter.in_position = True

                # We can't use .pop() here, as that would change the list's size.
                remaining_secret[index] = "*"

        # Now we look for yellows.
        for index in range(WORD_LENGTH):
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

        The word is transformed into uppercase and checked for errors.

        Args:
            word: A string to guess.

        Returns:
            A list of 'Letter' objects.

        Raises:
            GuessLengthError: If the word is not of the expected length.
            GuessNotFoundError: If the word is not present in the dictionary.
        """
        # Prevent additional guesses if this puzzle is solved.
        if self.is_solved:
            return []

        # Ensures word is in uppercase.
        word = word.upper()

        # Check for errors
        self.validate_guess(word)

        # Save current guess.
        letters = self._compare(word)
        self.attempts.append(word)
        self.guesses.append(letters)
        return letters

    def validate_guess(self, word: str) -> None:
        """Check if the word is a valid guess.

        Args:
            word: The word to check

        Raises:
            GuessLengthError: If the word is not of the expected length.
            GuessNotFoundError: If the word is not present in the dictionary.
        """
        word = word.upper()

        if len(word) != WORD_LENGTH:
            raise GuessLengthError(f"Guesses must be '{WORD_LENGTH}' characters long.")

        if not self.locale.find(word):
            raise GuessNotFoundError(f"The word '{word}' is not present in the dictionary.")
