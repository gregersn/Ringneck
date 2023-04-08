from dataclasses import dataclass
from enum import Enum, unique
from typing import Any


@unique
class TokenType(Enum):
    # Operators
    PLUS = '+'
    MINUS = '-'
    SLASH = '/'
    STAR = '*'

    EQUAL = '='

    DOLLAR = '$'
    DOT = '.'
    COLON = ':'
    COMMA = ','
    HASH = '#'

    GREATER = '>'
    GREATER_EQUAL = '>='

    LESS = '<'
    LESS_EQUAL = '<='

    LEFT_PAREN = '('
    RIGHT_PAREN = ')'

    EQUAL_EQUAL = '=='
    BANG_EQUAL = '!='

    LEFT_BRACE = '{'
    RIGHT_BRACE = '}'

    LEFT_BRACKET = '['
    RIGHT_BRACKET = ']'

    # Literals
    NUMBER = 'number'
    STRING = 'string'
    IDENTIFIER = 'identifier'

    EOL = 'EOL'
    EOF = 'EOF'


@dataclass
class Token:
    tokentype: TokenType
    lexeme: str
    literal: Any
    line: int
    column: int

    def __str__(self):
        return f"{self.line}:{self.column} {self.tokentype.name} {repr(self.lexeme)} {self.literal}"
