from dataclasses import dataclass

from ringneck.ast.base import Node, Visitor, VisitorType
from ringneck.ast import expression


class StatementVisitor(Visitor[VisitorType]):
    ...


@dataclass
class Statement(Node):
    ...


@dataclass
class Expression(Statement):
    expr: expression.Expression
