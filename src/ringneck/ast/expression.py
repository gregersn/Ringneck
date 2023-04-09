from dataclasses import dataclass
from typing import Any, List as TList

from ringneck.ast.base import Node, Visitor, VisitorType
from ..tokens import Token


class ExpressionVisitor(Visitor[VisitorType]):
    ...


@dataclass
class Expression(Node):
    ...


@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression


@dataclass
class Grouping(Expression):
    expression: Expression


@dataclass
class Literal(Expression):
    value: Any


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression


@dataclass
class Variable(Expression):
    name: Token


@dataclass
class VariableIterator(Expression):
    prefix: Expression
    iterator: 'List'


@dataclass
class Assign(Expression):
    name: Token
    value: Any


@dataclass
class AssignIterator(Expression):
    iterator: VariableIterator
    value: Any


@dataclass
class KeyDatum(Expression):
    key: Expression
    datum: Expression


@dataclass
class Dict(Expression):
    values: TList[KeyDatum]


@dataclass
class List(Expression):
    values: TList[Expression]


@dataclass
class Call(Expression):
    callee: Expression
    paren: Token
    arguments: TList[Expression]
