"""
Custom Exception to makes Error Handling easier.
"""


class InvalidKwargs(Exception):
    pass


class InvalidDB(Exception):
    pass


class InvalidGuild(Exception):
    pass


class InvalidChoice(Exception):

    def __init__(self, choice: list):
        self.correct = choice


class NotEligible(Exception):

    def __init__(self, user):
        self.user = user


class NotBanned(Exception):

    def __init__(self, uname):
        self.uname = uname
