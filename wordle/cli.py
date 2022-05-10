import sys
from argparse import ArgumentParser
from typing import List

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel

from wordle import Wordle, WORD_LENGTH, Guess
from wordle.locale import Locale
from wordle.modes import Mode
from wordle.exceptions import WordleException


console = Console()


# TODO: Create a `Puzzle` class to chain operations requiring Columns, Panels, and Puzzles.
# TODO: Use `click` instead of `argparse`.


def start_wordle() -> None:
    mode = Mode.from_name(args.mode)
    locale = Locale(args.locale)
    secrets = locale.get_secrets(amount=mode.puzzles_amount)

    puzzles = [Wordle(s, mode=mode, locale=locale) for s in secrets]
    print_empty_board(puzzles)

    attempt = 1
    previous_guesses = []
    while attempt <= mode.max_guesses:
        try:
            word = console.input("\n[bold]Type a word: [/]").upper()
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
        colored += f" [bold {letter.color}]{letter.char}[/] "

    return colored


parser = ArgumentParser()
parser.add_argument(
    "-m",
    "--mode",
    action="store",
    type=str,
    choices=["solo", "duo", "quad"],
    default="solo",
    help="The desired game mode.",
)
parser.add_argument(
    "-d",
    "--debug",
    action="store_true",
    default=False,
    help="Activates debug mode. This shows the secret word in the title of each board.",
)
parser.add_argument(
    "-a",
    "--align",
    action="store",
    type=str,
    choices=["left", "center", "right"],
    default="center",
    help="Where to align the boards on the screen.",
)
parser.add_argument(
    "-l",
    "--locale",
    action="store",
    type=str,
    choices=["en_us", "pt_br"],
    default="en_us",
    help="Which language to use for the words.",
)
args = parser.parse_args()

if __name__ == "__main__":
    start_wordle()
