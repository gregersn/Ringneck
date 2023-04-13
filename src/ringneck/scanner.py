from typing import Any, List
from ringneck.tokens import Token, TokenType, keywords
from ringneck.error_handler import ErrorHandler


class Scanner:
    source: str
    tokens: List[Token]

    _start: int = 0
    _current: int = 0
    _line: int = 1
    _column: int = 0

    def __init__(self, source: str):
        self.source = source

    def scan_tokens(self) -> List[Token]:
        self.tokens = []

        while not self.is_at_end():
            # The next token starts at the current location.
            self._start = self._current

            # Scan out the next token.
            self.scan_token()

        # End of source.
        self.tokens.append(
            Token(TokenType.EOF, "\0", None, self._line, self._current))

        return self.tokens

    def scan_token(self):
        char = self.advance()
        if char == '+':
            return self.add_token(TokenType.PLUS, '+')
        if char == '-':
            return self.add_token(TokenType.MINUS, '-')
        if char == '*':
            return self.add_token(TokenType.STAR, '*')
        if char == '/':
            return self.add_token(TokenType.SLASH, '/')

        if char == '%':
            return self.add_token(TokenType.PERCENT, '%')

        if char == '<':
            if self.peek() == '=':
                self.advance()
                return self.add_token(TokenType.LESS_EQUAL, '<=')
            return self.add_token(TokenType.LESS, '<')
        if char == '>':
            if self.peek() == '=':
                self.advance()
                return self.add_token(TokenType.GREATER_EQUAL, '>=')
            return self.add_token(TokenType.GREATER, '>')

        if char == '(':
            return self.add_token(TokenType.LEFT_PAREN, '(')
        if char == ')':
            return self.add_token(TokenType.RIGHT_PAREN, ')')
        if char == '{':
            return self.add_token(TokenType.LEFT_BRACE, '{')
        if char == '}':
            return self.add_token(TokenType.RIGHT_BRACE, '}')
        if char == '[':
            return self.add_token(TokenType.LEFT_BRACKET, '[')
        if char == ']':
            return self.add_token(TokenType.RIGHT_BRACKET, ']')

        if char == '=':
            if self.peek() == '=':
                self.advance()
                return self.add_token(TokenType.EQUAL_EQUAL, '==')
            return self.add_token(TokenType.EQUAL, char)

        if char == '!':
            if self.peek() == '=':
                self.advance()
                return self.add_token(TokenType.BANG_EQUAL, '!=')

        if char == '?':
            if self.peek() == '=':
                self.advance()
                return self.add_token(TokenType.MAYBE_EQUAL, '?=')

        if char == '.':
            return self.add_token(TokenType.DOT, char)

        if char == ':':
            return self.add_token(TokenType.COLON, char)

        if char == ',':
            return self.add_token(TokenType.COMMA, char)

        if char == '#':
            return self.comment()

        if char in ['"', "'"]:
            return self.string(char)

        if char.isdigit():
            return self.number()

        if char.isalpha() or char == '$':
            return self.identifier()

        if char in [' ', '\t']:
            return

        if char == '\n':
            if self._column > 1:
                self.add_token(TokenType.EOL)
            while self.peek() == '\n':
                self.advance()
                self.advance_line()
            self.advance_line()
            return

        ErrorHandler.report(self._line, self._column,
                            f"Unexepected character: {char}")

    def comment(self):
        while self.peek() != '\n':
            self.advance()
        self.advance_line()
        self.advance()
        return

    def advance_line(self):
        self._line += 1
        self._column = 0

    def string(self, quotation: str):
        while self.peek() != quotation and not self.is_at_end():
            if self.peek() == '\n':
                self.advance_line()
            self.advance()

        self.advance()

        self.add_token(TokenType.STRING,
                       self.source[self._start + 1:self._current - 1])
        return

    def number(self):
        is_float = False
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            is_float = True
            while self.peek().isdigit():
                self.advance()

        if is_float:
            self.add_token(TokenType.NUMBER, float(
                self.source[self._start:self._current]))
        else:
            self.add_token(TokenType.NUMBER, int(
                self.source[self._start:self._current], 10))

    def identifier(self):
        while self.peek().isalnum() or self.peek() in ['_', '.']:
            self.advance()

        identifier = self.source[self._start:self._current]
        identifier_type = keywords.get(identifier, TokenType.IDENTIFIER)
        self.add_token(identifier_type, identifier)

    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self._current]

    def peek_next(self):
        if self._current + 1 >= len(self.source):
            return '\0'

        return self.source[self._current + 1]

    def add_token(self, _type: TokenType, literal: Any = None):
        self.tokens.append(Token(
            _type, self.source[self._start:self._current], literal, self._line, self._column))

    def advance(self):
        char = self.source[self._current]
        self._current += 1
        self._column += 1
        return char

    def is_at_end(self):
        return self._current >= len(self.source)
