
from dataclasses import dataclass

from typing import List

from ringneck.tokens import Token


@dataclass
class Error:
    line: int
    column: int
    msg: str


class ErrorHandler:
    errors: List[Error] = []

    @classmethod
    def report(cls, line: int, column: int, msg: str):
        cls.errors.append(Error(line, column, msg))

    @classmethod
    def error(cls, token: Token, msg: str):
        cls.errors.append(Error(token.line, token.column, msg))

    @classmethod
    def reset(cls):
        cls.errors = []

    @classmethod
    @property
    def had_error(cls):
        return len(cls.errors) > 0

    @classmethod
    def runtime_error(cls, error: Exception):
        raise error
