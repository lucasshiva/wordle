from argparse import ArgumentParser

from wordle.modes import Mode


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "-m", "--mode", action="store", type=str, choices=["solo", "duo", "quad"], default="solo"
    )

    args = parser.parse_args()
    mode = Mode.from_name(args.mode)
    start_wordle(mode)


def start_wordle(mode: Mode) -> None:
    print(f"You are playing Wordle on {mode.name} mode.")


if __name__ == "__main__":
    main()
