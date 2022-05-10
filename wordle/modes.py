from dataclasses import dataclass

default_settings = {
    "solo": {"max_guesses": 6, "puzzles_amount": 1},
    "duo": {"max_guesses": 7, "puzzles_amount": 2},
    "quad": {"max_guesses": 9, "puzzles_amount": 4},
}


@dataclass
class Mode:
    name: str
    max_guesses: int
    puzzles_amount: int

    @classmethod
    def from_name(cls, name: str) -> "Mode":
        """Return an instance of `Mode` from a string."""
        if name not in default_settings:
            raise ValueError(f"Mode {name} not found.")

        mode_settings = default_settings[name]
        return cls(name=name, **mode_settings)
