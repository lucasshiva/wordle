import random
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Set, Union

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel

from wordle import Wordle
from wordle.modes import Mode
from wordle.wordle import Guess

console = Console()


# TODO: Create a `Puzzle` class to chain operations requiring Columns, Panels, and Puzzles.
# TODO: Use `click` instead of `argparse`.


def start_wordle() -> None:
    mode = Mode.from_name(args.mode)
    words = get_words("wordle/data/words.txt")
    secrets = get_secrets(words, amount=mode.puzzles_amount)
    puzzles = [Wordle(s, mode=mode) for s in secrets]

    print_empty_board(puzzles)
    counter = 1
    while counter <= mode.max_guesses:
        try:
            word = console.input("\n[bold]Type a word: [/]").upper()
            if word not in words:
                console.print(f"The word {word} is invalid.", style="red")
                continue
        except KeyboardInterrupt:
            sys.exit()
        else:
            console.clear()
            panels: List[Panel] = []
            for puzzle in puzzles:
                try:
                    puzzle.guess(word)
                except ValueError as e:
                    console.print(e, style="red")
                    continue
                panels.append(get_panel(puzzle))

            # Update the boards
            console.print(Columns(panels), justify=args.align)

            # Only check if the user won after updating the board.
            if all([p.is_solved for p in puzzles]):
                console.print("You won!", style="bold green")
                sys.exit()

            counter += 1

    secrets = [s.secret for s in puzzles]
    if mode.puzzles_amount > 1:
        text = f"[bold red]You lost![/] The secret was: [bold blue]{secrets[0]}[/]"
    else:
        text = f"[bold red]You lost![/] The secrets were: [bold blue]{' ,'.join(secrets)}[/]"
    console.print(text)


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
            stars_line = f" {char} " * puzzle.WORD_LENGTH + "\n"
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
    panel_title = f"[bold blue]{wordle.secret}[/]" if args.debug else None
    panel_content = ""
    for guess in wordle.guesses:
        colored_line = get_colored_string(guess) + "\n"
        panel_content += colored_line

    # We don't write the filler lines (and following guesses) for a wordle we've solved.
    # We also add a green 'OK' to the bottom of the panel.
    if wordle.is_solved:
        subtitle = "[bold green]OK[/]"
        panel_content += "\n" * wordle.remaining_attempts
    else:
        subtitle = None
        for _ in range(wordle.remaining_attempts):
            stars_line = " * " * wordle.WORD_LENGTH + "\n"
            panel_content += stars_line

    return Panel(panel_content[:-1], title=panel_title, subtitle=subtitle)


def get_colored_string(guess: Guess) -> str:
    """Return a valid `rich` colored string for a guess."""
    colored = ""

    for letter in guess:
        colored += f" [bold {letter.color}]{letter.char}[/] "

    return colored


def get_words(path: Union[str, Path]) -> Set[str]:
    """Fetch words from a text file.

    Each line is read as a whole word and words are transformed into uppercase.
    """
    words = set()
    with open(path, "r") as f:
        for line in f.readlines():
            words.add(line.strip().upper())

    return words


def get_secrets(words: Union[Set[str], List[str]], amount: int = 1) -> List[str]:
    """Get an amount of unique strings from a list or a set.

    Args:
        words: A list or a set of strings.
        amount: The amount of secret words to return.

    Returns:
        A list of secret words.
    """
    # No need to check if is a set or not.
    word_list = list(words)
    previous = ""

    secrets: List[str] = []
    while len(secrets) != amount:
        secret = random.choice(word_list)
        if secret == previous:  # Skip duplicate.
            continue

        secrets.append(secret)
        previous = secret

    return secrets


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
args = parser.parse_args()

if __name__ == "__main__":
    start_wordle()
