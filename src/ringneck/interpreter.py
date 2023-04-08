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
        if global_variables:
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
        if expr.operator.tokentype == TokenType.PLUS:
            return expr.left.accept(self) + expr.right.accept(self)

    def visit_Expression_Statement(self, stmt: statement.Expression):
        return self.evaluate(stmt.expr)

    def visit_Assign_Expression(self, expr: expression.Assign):
        self.set(expr.name.literal, self.evaluate(expr.value))

    def visit_Variable_Expression(self, expr: expression.Variable):
        return self.get(expr.name.literal)

    def visit_Dict_Expression(self, expr: expression.Dict):
        output: Dict[Any, Any] = {}

        for entry in expr.values:
            key = entry.key.accept(self)
            value = entry.datum.accept(self)

            output[key] = value

        return output

    def visit_List_Expression(self, expr: expression.List):
        output: List[Any] = []
        for entry in expr.values:
            value = entry.accept(self)
            output.append(value)

        return output

    def visit_Call_Expression(self, expr: expression.Call):
        callee = self.evaluate(expr.callee)

        arguments: List[Any] = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        return callee(*arguments)

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
