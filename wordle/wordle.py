import sys
from argparse import ArgumentParser

from wordle.board import Board
from wordle.console import console
from wordle.exceptions import WordleException
from wordle.locale import Locale
from wordle.modes import Mode


def start_wordle() -> None:
    mode = Mode.from_name(args.mode)
    locale = Locale(args.locale)
    board = Board(mode=mode, locale=locale, debug=args.debug)

    board.draw()

    attempt = 1
    previous_guesses = []
    while attempt <= mode.max_guesses:
        try:
            word = console.input("[bold]Guess: [/]").upper()
        except KeyboardInterrupt:
            sys.exit()
        except UnicodeDecodeError as e:
            console.print(f"Invalid guess: {e}", style="red")
            continue

        # We don't want to let the user guess the same word multiple times.
        if word in previous_guesses:
            console.print(f"The word '{word}' has already been guessed.", style="red")
            continue

        try:
            board.guess(word)
        except WordleException as e:  # works for both exceptions.
            console.print(e, style="red")
            continue
        else:
            # We know it's a valid guess, add it to the list.
            previous_guesses.append(word)

        # Update the board on the screen.
        board.draw()

        # Only check if the user won after updating the board.
        if board.is_solved():
            console.print("You won!", style="bold green")
            sys.exit()

        attempt += 1

    # Only runs when the user is out of guesses.
    console.print("[bold red]You lost![/]")


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
