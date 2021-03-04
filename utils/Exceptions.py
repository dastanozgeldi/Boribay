from discord.ext import commands


class NoReactionsPassed(commands.CommandInvokeError):
    """Specific exception for the trivia command."""
    pass


class CalcError(Exception):
    """Raised when parsing the task was unsuccessful."""

    def __init__(self, char):
        self.exc = f'Inadmissable character in the task: `{char}`'


class KeywordAlreadyTaken(Exception):
    """Raised when the keyword that is created by user is already taken."""
    pass


class UndefinedVariable(Exception):
    """Raised when the called variable does not exist."""

    def __init__(self, variable):
        self.exc = f'Wrong variable name given: `{variable}`.'


class Overflow(Exception):
    """Raised when the given expression output was too big."""
    pass


class UnclosedBrackets(Exception):
    """Raised when the given expression has unclosed brackets."""
    pass


class EmptyBrackets(Exception):
    """Raised when the given expression has empty or unused brackets."""
    pass


class TooManyOptions(commands.CommandError):
    """Raised when there were too many options on a poll."""
    pass


class NotEnoughOptions(commands.CommandError):
    """Raised when either there was only 1 options or no options."""
    pass


class NoChannelProvided(commands.CommandError):
    """Error raised when no suitable voice channel was supplied."""
    pass


class IncorrectChannelError(commands.CommandError):
    """Error raised when commands are issued outside of the players session channel."""
    pass
