import json
import random
from pathlib import Path
from typing import Any, Dict, List, Set
from typing_extensions import Literal


DATA_DIR = Path(__file__).parent.resolve() / "data"


class Locale:
    def __init__(self, locale: Literal["en_us", "pt_br"] = "en_us") -> None:
        self.locale = locale

        # Wordlist
        self.secret_words: Set[str]
        self.dict_words: Set[str]

        # For locales that use accented words.
        # This is a mapping where the key is the unaccented word and the value is the original word.
        self.unaccented_words: Dict[str, str]

        self._load_words()

    def _load_words(self) -> None:
        """Load words for the current locale.

        The words are transformed into uppercase when read.
        """
        with open(DATA_DIR / f"{self.locale}.json") as f:
            data: Dict[str, Any] = json.load(f)

        self.secret_words = {w.upper() for w in data["secret_words"]}
        self.dict_words = {w.upper() for w in data["dict_words"]}
        self.unaccented_words = {
            key.upper(): value.upper() for key, value in data["unaccented"].items()
        }

    def get_secrets(self, amount: int = 1) -> List[str]:
        """Return an specified amount of secret words."""
        previous = ""
        secrets: List[str] = []
        while len(secrets) != amount:
            secret = random.choice(list(self.secret_words))
            if secret == previous:  # Skip duplicate.
                continue

            secrets.append(secret)
            previous = secret

        return secrets

    def find(self, word: str) -> bool:
        """Check if the word is present in the word list."""
        # Ensures the word is in uppercase before any operations.
        word = word.upper()

        if word in self.dict_words:
            return True

        elif word in self.secret_words:
            return True

        elif self.unaccented_words.get(word):
            return True

        return False
