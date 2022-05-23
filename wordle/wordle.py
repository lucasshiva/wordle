from typing import Dict, List, Union

from rich.panel import Panel
from unidecode import unidecode

from wordle.exceptions import GuessLengthError, GuessNotFoundError
from wordle.guess import Guess
from wordle.letter import Letter
from wordle.locale import Locale
from wordle.modes import Mode

WORD_LENGTH = 5


class Wordle:
    def __init__(self, id: int, secret: str, mode: Mode, locale: Locale) -> None:
        self.id = id
        self.secret = secret.upper()  # Ensure the secret is in uppercase.
        self.mode = mode
        self.locale = locale

        # Keep track of all the guesses.
        self.guesses: List[Guess] = []

        # Same as above, but leave guesses as strings.
        self.attempts: List[str] = []

    def _compare(self, word: str) -> List[Letter]:
        """Compare a word with the secret word."""
        letters = [Letter(char) for char in word]
        remaining_secret = list(unidecode(self.secret))

        # Get the greens first.
        for index in range(WORD_LENGTH):
            letter = letters[index]
            if letter.unaccented_char == remaining_secret[index]:
                letter.in_position = True

                # We can't use .pop() here, as that would change the list's size.
                remaining_secret[index] = "*"

        # Now we look for yellows.
        for index in range(WORD_LENGTH):
            letter = letters[index]
            if letter.unaccented_char in remaining_secret:
                letter.in_word = True
                remaining_secret.remove(letter.unaccented_char)

        return letters

    @property
    def is_solved(self) -> bool:
        """Check whether the last guess was correct."""
        return (len(self.attempts) > 0) and (self.attempts[-1] == self.secret)

    @property
    def remaining_attempts(self) -> int:
        """Return the amount of remaining attempts."""
        return self.mode.max_guesses - len(self.attempts)

    def guess(self, word: str) -> Union[Guess, None]:
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
            return None

        word = self.validate_guess(word.upper())
        letters = self._compare(word)
        guess = Guess(word, letters)

        # Store the current guess
        self.attempts.append(word)
        self.guesses.append(guess)

        return guess

    def validate_guess(self, word: str) -> str:
        """Search for the word and check if it's a valid guess.

        If `word` is an unnacented word and the locale supports accented words, then this will
        return the accented word, if an equivalent is found.

        Args:
            word: The string to validate.

        Returns:
            The word found.

        Raises:
            GuessLengthError: If the word is not of the expected length.
            GuessNotFoundError: If the word is not present in the dictionary.
        """
        word = word.upper()

        if len(word) != WORD_LENGTH:
            raise GuessLengthError(f"Guesses must be '{WORD_LENGTH}' characters long.")

        if not self.locale.find(word):
            raise GuessNotFoundError(f"The word '{word}' is not present in the dictionary.")

        return self.locale.word_found

    def get_panel(self, debug: bool = False) -> Panel:
        """Create a `Panel` for the current puzzle.

        Args:
            debug: Whether to show debug information in the panel.

        Returns:
            A `Panel` containing all the guesses and remaining attempts for the puzzle.
        """
        # Shows the secret word in the top of each puzzle.
        panel_title = f"[bold blue]{self.id}[/]"

        # Shows the status (OK, FAIL) in the bottom of each puzzle.
        subtitle = ""

        border_style = ""

        if (self.remaining_attempts == 0 and not self.is_solved) or debug:
            panel_title += f" - [bold blue]{self.secret}[/]"

        if self.remaining_attempts == 0:
            subtitle = "[bold red]FAIL[/]"
            border_style = "bold red"

        panel_content = ""
        for guess in self.guesses:
            colored_line = guess.as_colored_string() + "\n"
            panel_content += colored_line

        # Don't write the filler lines (and following guesses) for a wordle we've solved.
        if self.is_solved:
            subtitle = "[bold green]OK[/]"
            border_style = "bold green"
            panel_content += "\n" * self.remaining_attempts
        else:
            for _ in range(self.remaining_attempts):
                stars_line = " * " * WORD_LENGTH + "\n"
                panel_content += stars_line

        return Panel(
            panel_content[:-1], title=panel_title, subtitle=subtitle, border_style=border_style
        )

    def get_keyboard(self) -> Panel:
        """Get a keyboard for the current puzzle."""
        colored_keys: Dict[str, str] = {}
        title = f"[bold blue]{self.id}[/]"
        subtitle = ""
        border_style = ""

        if self.is_solved:
            subtitle = "[bold green]OK[/]"
            border_style = "bold green"

        elif self.remaining_attempts == 0:
            subtitle = "[bold red]FAIL[/]"
            border_style = "bold red"

        else:
            colored_keys = self._get_keyboard_colors()

        rows = [
            ["Q", "W", "E", "R", "T"],
            ["Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G"],
            ["H", "J", "K", "L", "Z"],
            ["*", "X", "C", "V", "*"],
            ["*", "B", "N", "M", "*"],
        ]

        panel_content = ""
        for row in rows:
            for char in row:
                if char in colored_keys:
                    panel_content += f" {colored_keys[char]} "
                else:
                    panel_content += f" [bold]{char}[/] "

            panel_content += "\n"

        return Panel(panel_content[:-1], title=title, subtitle=subtitle, border_style=border_style)

    def _get_keyboard_colors(self) -> Dict[str, str]:
        keys: Dict[str, str] = {}

        for guess in self.guesses:
            for letter in guess.letters:
                # Greens first.
                if letter.in_position:
                    keys[letter.unaccented_char] = letter.rich_color
                    continue

                # Only add the yellows if it's not a green.
                if letter.in_word and letter.unaccented_char not in keys:
                    keys[letter.unaccented_char] = letter.rich_color
                    continue

                if not letter.in_word:
                    keys[letter.unaccented_char] = letter.rich_color
                    continue

        return keys
