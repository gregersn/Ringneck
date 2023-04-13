"""Ringneck parser."""
from typing import List
from ringneck.ast import expression, statement
from ringneck.error_handler import ErrorHandler

from ringneck.tokens import Token, TokenType


class Parser:
    tokens: List[Token]
    current: int = 0

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def match(self, *args: TokenType) -> bool:
        for tokentype in args:
            if self.check(tokentype):
                self.advance()
                return True

        return False

    def check(self, tokentype: TokenType):
        if self.is_at_end():
            return False

        return self.peek().tokentype == tokentype

    def advance(self):
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def is_at_end(self):
        return self.peek().tokentype == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def parse(self):
        statements: List[statement.Statement] = []
        while not self.is_at_end():
            statements.append(self.statement())
            while self.match(TokenType.EOL):
                pass

        return statements

    def statement(self):
        return self.expression_statement()

    def expression_statement(self):
        expr = self.parse_expression()

        if not self.is_at_end():
            self.consume(
                TokenType.EOL, f"Expect newline after expression, got {self.peek().tokentype}")
        return statement.Expression(expr)

    def expression_list(self):
        expr = self.equality()
        if self.peek().tokentype == TokenType.COMMA:
            expr_list = [expr]
            while self.match(TokenType.COMMA):
                expr_list.append(self.equality())

            if self.peek().tokentype != TokenType.RIGHT_PAREN:
                return expression.Tuple(expr_list)
            expr = expression.ExpressionList(expr_list)
        return expr

    def parse_expression(self):
        return self.assignment()

    def assignment(self) -> expression.Expression:
        expr = self.expression_list()

        if self.match(TokenType.EQUAL, TokenType.MAYBE_EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, (expression.Tuple, expression.List)):
                assert isinstance(value, expression.Tuple)
                assert len(expr.values) == len(value.values)
                return expression.MultiAssign(expr, equals, value)
            if isinstance(expr, expression.Variable):
                name = expr.name
                return expression.Assign(name, equals, value)
            if isinstance(expr, expression.VariableIterator):
                return expression.AssignIterator(expr, equals, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def equality(self):
        expr = self.logical()

        if self.peek().tokentype == TokenType.IF:
            self.consume(TokenType.IF, "Expected conditional")
            condition = self.equality()
            other = None

            if self.peek().tokentype == TokenType.ELSE:
                self.consume(TokenType.ELSE,
                             f"Expected else, got {self.peek().tokentype}")
                other = self.parse_expression()

            return expression.Conditional(expr, condition, other)

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.logical()
            expr = expression.Binary(expr, operator, right)

        return expr

    def logical(self):
        expr = self.comparison()

        while (self.match(TokenType.AND, TokenType.OR)):
            operator = self.previous()
            right = self.comparison()
            expr = expression.Binary(expr, operator, right)

        return expr

    def comparison(self):
        expr = self.term()

        while (self.match(TokenType.GREATER, TokenType.GREATER_EQUAL,
                          TokenType.LESS, TokenType.LESS_EQUAL)):
            operator = self.previous()
            right = self.term()
            expr = expression.Binary(expr, operator, right)

        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = expression.Binary(expr, operator, right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = expression.Binary(expr, operator, right)

        return expr

    def unary(self) -> expression.Expression:
        if self.match(TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return expression.Unary(operator, right)
        if self.match(TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            return expression.Starred(operator, right)
        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break

        return expr

    def finish_call(self, callee: expression.Expression):
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.equality())
            while self.match(TokenType.COMMA):
                arguments.append(self.equality())

        paren = self.consume(TokenType.RIGHT_PAREN,
                             "Expected ')' after arguments")

        return expression.Call(callee, paren, expression.ExpressionList(arguments))

    def primary(self):
        if self.match(TokenType.FALSE):
            return expression.Literal(False)

        if self.match(TokenType.TRUE):
            return expression.Literal(True)

        if self.match(TokenType.NOT):
            return expression.Literal('not')

        if self.match(TokenType.IDENTIFIER):
            if self.peek().tokentype == TokenType.LEFT_BRACKET:
                prefix = self.previous()
                iterator = self.primary()
                return expression.VariableIterator(prefix, iterator)

            return expression.Variable(self.previous())

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return expression.Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression_list()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            if isinstance(expr, expression.ExpressionList):
                return expression.Tuple(expr.expressions)
            return expression.Grouping(expr)

        if self.match(TokenType.LEFT_BRACKET):
            return self.list()

        if self.match(TokenType.LEFT_BRACE):
            return self.dictionary()

        if self.match(TokenType.PERCENT):
            return expression.IteratorValue(self.previous())

        raise self.error(self.peek(), "Expect expression")

    def dictionary(self):
        data_pairs: List[expression.KeyDatum] = []
        while not self.peek().tokentype == TokenType.RIGHT_BRACE:

            while self.check(TokenType.EOL):
                self.advance()

            key = self.parse_expression()
            self.consume(TokenType.COLON, "Expect colon")
            value = self.equality()
            data_pairs.append(expression.KeyDatum(key, value))
            if self.peek().tokentype == TokenType.COMMA:
                self.consume(TokenType.COMMA, "Expected comma")

            while self.check(TokenType.EOL):
                self.advance()

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' to close dict")
        return expression.Dict(data_pairs)

    def list(self):
        if self.peek().tokentype == TokenType.RIGHT_BRACKET:
            self.consume(TokenType.RIGHT_BRACKET,
                         "Expected ']' to close an empty list.")
            return expression.List(expression.ExpressionList([]))
        expr = self.expression_list()
        self.consume(TokenType.RIGHT_BRACKET, "Expect ']' to close list")
        if isinstance(expr, expression.Starred):
            return expression.List(expr)
        return expression.List(expr.values)

    def consume(self, tokentype: TokenType, message: str):
        if self.check(tokentype):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str):
        ErrorHandler.error(token, message)
        return ParserError(token, message)

    def synchronize(self):
        # TODO: This is where we should try to
        # find the start of a new statement.
        self.advance()

        while not self.is_at_end():
            if self.previous().tokentype == TokenType.EOL:
                return

            if self.peek().tokentype in []:
                return

            self.advance()


class ParserError(RuntimeError):
    ...
