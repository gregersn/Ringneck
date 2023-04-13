from typing import Any, List
from ringneck.ast.base import VisitorType, Visitor

from ringneck.ast.expression import Binary, Expression, Grouping, Literal
from ringneck.ast import statement, expression


class ASTPrinter(Visitor[VisitorType]):
    def print(self, program: List[Any]):
        output: List[str] = []
        for step in program:
            output.append(str(step.accept(self)))
        return output

    def parenthesize(self, name: str, *exprs: Expression):
        output: List[str] = []

        output.append(f"({name}")
        for expr in exprs:
            output.append(" ")
            output.append(str(expr.accept(self)))
        output.append(")")

        return "".join(output)

    def visit_Literal_Expression(self, literal: Literal):
        return literal.value

    def visit_Grouping_Expression(self, grouping: Grouping):
        return self.parenthesize("grouping", grouping.expression)

    def visit_Binary_Expression(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_Expression_Statement(self, stmt: statement.Expression):
        return str(stmt.expr.accept(self))

    def visit_Assign_Expression(self, expr: expression.Assign):
        return self.parenthesize(f'assign {expr.name.literal}', expr.value)

    def visit_AssignIterator_Expression(self, expr: expression.AssignIterator):
        return self.parenthesize(f'assign {expr.iterator.accept(self)}', expr.value)

    def visit_KeyDatum_Expression(self, expr: expression.KeyDatum):
        return f"{expr.key.accept(self)}: {expr.datum.accept(self)}"

    def visit_Dict_Expression(self, expr: expression.Dict):
        return f"(dict {', '.join([v.accept(self) for v in expr.values])})"

    def visit_List_Expression(self, expr: expression.List):
        if isinstance(expr.values, expression.Starred):
            return expr.values.accept(self)

        if isinstance(expr.values, expression.ExpressionList):
            return f"(list {', '.join([str(v.accept(self)) for v in expr.values.expressions])})"

        return f"(list {', '.join([str(v.accept(self)) for v in expr.values])})"

    def visit_Variable_Expression(self, expr: expression.Variable):
        return f"{expr.name.literal}"

    def visit_VariableIterator_Expression(self, expr: expression.VariableIterator):
        return f"{expr.prefix.literal}{expr.iterator.accept(self)}"

    def visit_Conditional_Expression(self, expr: expression.Conditional):
        return f"(if {expr.left.accept(self)} {expr.condition.accept(self)} {expr.right.accept(self)})"

    def visit_Call_Expression(self, expr: expression.Call):
        return f"(call {expr.callee.accept(self)} {' '.join([str(arg.accept(self)) for arg in expr.arguments.expressions])})"

    def visit_MultiAssign_Expression(self, expr: expression.MultiAssign):
        return (f'(assign {expr.identifiers.accept(self)} {expr.values.accept(self)})')

    def visit_Tuple_Expression(self, expr: expression.Tuple):
        return f"(tuple {', '.join(str(v.accept(self)) for v in expr.values)})"

    def visit_ExpressionList_Expression(self, expr: expression.ExpressionList):
        return f"(expressionlist {', '.join(str(v.accept(self)) for v in expr.expressions)})"

    def visit_Starred_Expression(self, expr: expression.Starred):
        return self.parenthesize("starred", expr.value)
