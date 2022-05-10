class WordleException(Exception):
    pass


class GuessLengthError(WordleException):
    pass


class GuessNotFoundError(WordleException):
    pass
