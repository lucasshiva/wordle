import sys
from argparse import ArgumentParser
from typing import Dict, List

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel

from wordle import WORD_LENGTH, Guess, Wordle
from wordle.exceptions import WordleException
from wordle.letter import Letter
from wordle.locale import Locale
from wordle.modes import Mode

console = Console()


# TODO: Create a `Puzzle` class to chain operations requiring Columns, Panels, and Puzzles.
# TODO: Maybe use `click` instead of `argparse`?.


def start_wordle() -> None:
    mode = Mode.from_name(args.mode)
    locale = Locale(args.locale)
    secrets = locale.get_secrets(amount=mode.puzzles_amount)

    puzzles = [Wordle(s, mode=mode, locale=locale) for s in secrets]
    print_empty_board(puzzles)
    draw_keyboard(puzzles)

    attempt = 1
    previous_guesses = []
    while attempt <= mode.max_guesses:
        try:
            word = console.input("[bold]Guess: [/]").upper()
        except KeyboardInterrupt:
            sys.exit()

        try:
            puzzles[0].validate_guess(word)
        except WordleException as e:
            console.print(e, style="red")
            continue

        if word in previous_guesses:
            console.print(f"The word '{word}' has already been guessed.", style="red")
            continue
        else:
            previous_guesses.append(word)

        console.clear()
        panels: List[Panel] = []
        for puzzle in puzzles:
            # If the user guessed an unaccented word, `word_found` will be its accented version.
            # Else, `word_found` will be the same as the guess.
            word = puzzle.locale.word_found
            puzzle.guess(word)
            panels.append(get_panel(puzzle))

        # Update the boards
        console.print(Columns(panels), justify=args.align)
        draw_keyboard(puzzles)

        # Only check if the user won after updating the board.
        if all([p.is_solved for p in puzzles]):
            console.print("You won!", style="bold green")
            sys.exit()

        attempt += 1

    # Only runs when attempts equals zero.
    console.print("[bold red]You lost![/]")


# TODO: Find a way to merge this with `get_panel`.
def print_empty_board(puzzles: List[Wordle], char: str = "*") -> None:
    """Print an empty board.

    Args:
        puzzles: A list of `Wordle` objects.
        debug: Whether to show (True) the secret word or not (False).
        char: The character used as a placeholder for lines without words/guesses.
    """
    console.clear()

    panels: List[Panel] = []
    for puzzle in puzzles:
        # Add secret to the top of the panel if debug is set to True.
        panel_title = f"[bold blue]{puzzle.secret}[/]" if args.debug else None
        panel_content = ""
        for _ in range(puzzle.mode.max_guesses):
            stars_line = f" {char} " * WORD_LENGTH + "\n"
            panel_content += stars_line

        panels.append(Panel(panel_content.rstrip(), title=panel_title))

    console.print(Columns(panels), justify=args.align)


def get_panel(wordle: Wordle) -> Panel:
    """Create a `Panel` for the current wordle.

    Args:
        wordle: The `Wordle` object.

    Returns:
        A `Panel` containing all the guesses and remaining attempts for the `Wordle` object.
    """
    # Shows the secret word in the top of each puzzle.
    panel_title = None

    # Shows the status (OK, FAIL) in the bottom of each puzzle.
    subtitle = None

    if wordle.remaining_attempts == 0 or args.debug:
        panel_title = f"[bold blue]{wordle.secret}[/]"

    if wordle.remaining_attempts == 0:
        subtitle = "[bold red]FAIL[/]"

    panel_content = ""
    for guess in wordle.guesses:
        colored_line = get_colored_string(guess) + "\n"
        panel_content += colored_line

    # Don't write the filler lines (and following guesses) for a wordle we've solved.
    if wordle.is_solved:
        subtitle = "[bold green]OK[/]"
        panel_content += "\n" * wordle.remaining_attempts
    else:
        for _ in range(wordle.remaining_attempts):
            stars_line = " * " * WORD_LENGTH + "\n"
            panel_content += stars_line

    return Panel(panel_content[:-1], title=panel_title, subtitle=subtitle)


def get_colored_string(guess: Guess) -> str:
    """Return a valid `rich` colored string for a guess."""
    colored = ""

    for letter in guess:
        colored += f" {get_colored_letter(letter)} "

    return colored


def get_colored_letter(letter: Letter) -> str:
    """Return a valid `rich` colored string for a letter."""
    return f"[bold {letter.color}]{letter.char}[/]"


def draw_keyboard(puzzles: List[Wordle]) -> None:
    """Draw a keyboard on the screen."""
    colored_letters: Dict[str, str] = {}

    # invalid_letters = set()
    # valid_letters = set()
    greens = set()
    yellows = set()
    reds = set()

    for puzzle in puzzles:
        if len(puzzle.guesses) == 0:
            break

        if puzzle.is_solved:
            continue

        for guess in puzzle.guesses:
            for letter in guess:
                if letter.in_position:
                    colored_letters[letter.char.upper()] = get_colored_letter(letter)
                    greens.add(letter.char)
                    continue

                # Only add the yellows if it's not a green.
                if letter.in_word and letter.char not in colored_letters:
                    colored_letters[letter.char.upper()] = get_colored_letter(letter)
                    yellows.add(letter.char)
                    continue

                reds.add(letter.char)

    # Make sure only white letters stay are marked as invalid.
    for red in reds.copy():
        if red in greens or red in yellows:
            reds.remove(red)

    top_row = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]
    middle_row = ["", "A", "S", "D", "F", "G", "H", "J", "K", "L"]
    bottom_row = ["", " ", "Z", "X", "C", "V", "B", "N", "M"]
    rows = [top_row, middle_row, bottom_row]

    panel_content = ""
    for row in rows:
        for char in row:
            if char in reds:
                panel_content += f" [bold red]{char}[/] "
            elif char in colored_letters:
                panel_content += f" {colored_letters[char]} "
            else:
                panel_content += f" [bold]{char}[/] "

        panel_content += "\n"

    panel = Panel(panel_content[:-1], title="[bold blue]Keyboard[/]")
    console.print(Columns([panel]), justify="center")


parser = ArgumentParser()
parser.add_argument(
    "-d",
    "--debug",
    action="store_true",
    default=False,
    help="Show the secret word in the title of each puzzle",
)
parser.add_argument(
    "-m",
    "--mode",
    action="store",
    type=str,
    choices=["solo", "duo", "quad"],
    default="solo",
    help="The desired game mode (default: 'solo')",
)
parser.add_argument(
    "-a",
    "--align",
    action="store",
    type=str,
    choices=["left", "center", "right"],
    default="center",
    help="Where to align the puzzles on the screen (default: 'center')",
)
parser.add_argument(
    "-l",
    "--locale",
    action="store",
    type=str,
    choices=["en_us", "pt_br"],
    default="en_us",
    help="Which language to use for words (default: 'en_us')",
)
args = parser.parse_args()

if __name__ == "__main__":
    start_wordle()
