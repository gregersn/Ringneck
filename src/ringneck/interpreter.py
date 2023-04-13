from collections import ChainMap
from typing import Any, Dict, List, Mapping, MutableMapping, Optional


from ringneck.ast.expression import Binary, Expression, ExpressionVisitor, Grouping, Literal
from ringneck.ast import statement, expression
from ringneck.error_handler import ErrorHandler
from ringneck.tokens import TokenType


class Interpreter(ExpressionVisitor[Expression],
                  statement.StatementVisitor[statement.Statement]):

    globals: Optional[Any] = None

    def __init__(self, global_variables: Optional[Any] = None,
                 builtins: Optional[Dict[str, Any]] = None,
                 **kwargs: Any):
        super().__init__(**kwargs)
        if global_variables is not None:
            self.globals = global_variables
        self.builtins = builtins or {}

        self.state = ChainMap(self.builtins, self.state)

    def interpret(self, program: List[statement.Statement]):
        output: List[Any] = []
        try:
            for stmt in program:
                output.append(self.execute(stmt))
        except RuntimeError as error:
            ErrorHandler.runtime_error(error)

        return output

    def execute(self, stmt: statement.Statement):
        return stmt.accept(self)

    def evaluate(self, expr: Expression):
        return expr.accept(self)

    def visit_Literal_Expression(self, literal: Literal):
        return literal.value

    def visit_Grouping_Expression(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_Binary_Expression(self, expr: Binary):
        try:
            if expr.operator.tokentype == TokenType.PLUS:
                return expr.left.accept(self) + expr.right.accept(self)

            if expr.operator.tokentype == TokenType.MINUS:
                return expr.left.accept(self) - expr.right.accept(self)

            if expr.operator.tokentype == TokenType.STAR:
                left_value = expr.left.accept(self)
                right_value = expr.right.accept(self)
                return left_value * right_value

            if expr.operator.tokentype == TokenType.SLASH:
                return expr.left.accept(self) / expr.right.accept(self)

            if expr.operator.tokentype == TokenType.LESS:
                return expr.left.accept(self) < expr.right.accept(self)

            if expr.operator.tokentype == TokenType.LESS_EQUAL:
                return expr.left.accept(self) <= expr.right.accept(self)

            if expr.operator.tokentype == TokenType.GREATER:
                return expr.left.accept(self) > expr.right.accept(self)

            if expr.operator.tokentype == TokenType.GREATER_EQUAL:
                return expr.left.accept(self) >= expr.right.accept(self)

            if expr.operator.tokentype == TokenType.AND:
                return expr.left.accept(self) and expr.right.accept(self)

            if expr.operator.tokentype == TokenType.EQUAL_EQUAL:
                return expr.left.accept(self) == expr.right.accept(self)

            if expr.operator.tokentype == TokenType.BANG_EQUAL:
                return expr.left.accept(self) != expr.right.accept(self)
        except TypeError as exp:
            raise RuntimeError(
                f"Wrong types in expression at {expr.operator.line}, {expr.operator.column}") from exp

        raise RuntimeError(f"Unknown operator '{expr.operator.lexeme}'")

    def visit_Expression_Statement(self, stmt: statement.Expression):
        return self.evaluate(stmt.expr)

    def visit_Tuple_Expression(self, expr: expression.Tuple):
        return tuple([v.accept(self) for v in expr.values])

    def visit_Assign_Expression(self, expr: expression.Assign):
        if expr.operator.tokentype == TokenType.MAYBE_EQUAL:
            if self.get(expr.name.literal) is not None:
                return
        self.set(expr.name.literal, self.evaluate(expr.value))

    def visit_MultiAssign_Expression(self, expr: expression.MultiAssign):
        identifiers = [v.name.literal for v in expr.identifiers.values]
        for identifier, value in zip(identifiers, expr.values.values):
            self.set(f"{identifier}", self.evaluate(value))

    def visit_AssignIterator_Expression(self, expr: expression.AssignIterator):
        prefix = expr.iterator.prefix.literal
        iterator = expr.iterator.iterator.accept(self)

        for it in iterator:
            self.state['%'] = it
            self.set(f"{prefix}{it}", self.evaluate(expr.value))
        if '%' in self.state:
            del self.state['%']

    def visit_Variable_Expression(self, expr: expression.Variable):
        return self.get(expr.name.literal)

    def visit_IteratorValue_Expression(self, expr: expression.IteratorValue):
        return self.state.get(expr.token.lexeme, None)

    def visit_VariableIterator_Expression(self,
                                          expr: expression.VariableIterator):
        prefix = expr.prefix.literal
        iterator = expr.iterator.accept(self)

        return [self.get(f"{prefix}{it}") for it in iterator]

    def visit_Dict_Expression(self, expr: expression.Dict):
        output: Dict[Any, Any] = {}

        for entry in expr.values:
            key = entry.key.accept(self)
            value = entry.datum.accept(self)

            output[key] = value

        return output

    def visit_List_Expression(self, expr: expression.List):
        if isinstance(expr.values, expression.Starred):
            values = self.evaluate(expr.values)
            if values is None:
                raise RuntimeError(
                    f"Expected an iterable, got NoneType near {expr.values.operator.line} {expr.values.operator.column}")
            return list(values)

        if isinstance(expr.values, expression.ExpressionList):
            output: List[Any] = []
            for entry in expr.values.expressions:
                value = entry.accept(self)
                output.append(value)

            return output

        output: List[Any] = []
        for entry in expr.values:
            value = entry.accept(self)
            output.append(value)

        return output

    def visit_Call_Expression(self, expr: expression.Call):
        callee = self.evaluate(expr.callee)

        arguments: List[Any] = []
        for argument in expr.arguments.expressions:
            arguments.append(self.evaluate(argument))

        if hasattr(callee, '__globals__'):
            callee.__globals__['state'] = self.state
            callee.__globals__['globals'] = self.globals

        try:
            return callee(*arguments)
        except (AttributeError, TypeError) as exc:
            raise RuntimeError(f"Error in expression: {expr}") from exc

    def visit_Conditional_Expression(self, expr: expression.Conditional):
        if expr.condition.accept(self):
            return expr.left.accept(self)

        if expr.right is not None:
            return expr.right.accept(self)

    def visit_Starred_Expression(self, expr: expression.Starred):
        return self.evaluate(expr.value)

    def get(self, variable_address: str):
        parts = variable_address.split('.')
        if parts[0] == '$':
            if self.globals is None:
                self.globals = {}
            source = self.globals
            parts.pop(0)
        else:
            source = self.state

        result = source
        while parts:
            part = parts.pop(0)
            if hasattr(result, part):
                result = getattr(result, part)

            elif isinstance(result, Mapping):
                result = result.get(part)
        return result

    def set(self, variable_address: str, value: Any):
        parts = variable_address.split('.')
        if parts[0] == '$':
            if self.globals is None:
                self.globals = {}

            source = self.globals
            parts.pop(0)
        else:
            source = self.state

        result = source
        while len(parts) > 1:
            part = parts.pop(0)
            if isinstance(result, Mapping):
                result = result[part]
            else:
                result = getattr(result, part)

        if isinstance(result, MutableMapping):
            result[parts[0]] = value
        else:
            setattr(result, parts[0], value)
