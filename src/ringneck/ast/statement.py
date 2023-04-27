from dataclasses import dataclass
from typing import List, Optional

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


@dataclass
class If(Statement):
    condition: expression.Expression
    thenbranch: List['Statement']


@dataclass
class Repeat(Statement):
    count: int
    stmt: Statement
