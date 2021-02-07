"""
Custom Exception to makes Error Handling easier.
"""


class InvalidKwargs(Exception):
    pass


class InvalidDB(Exception):
    pass


class InvalidGuild(Exception):
    pass


class InvalidMessage(Exception):
    def __init__(self, text):
        self.text = text


class InvalidChoice(Exception):

    def __init__(self, choice: list):
        self.correct = choice


class NotEligible(Exception):

    def __init__(self, user):
        self.user = user


class NotBanned(Exception):

    def __init__(self, uname):
        self.uname = uname


class MissingRequiredParam(Exception):
    """
    Oops! Something is missing.
    """
    pass
