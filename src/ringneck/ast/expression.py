from dataclasses import dataclass
import operator
from typing import Any, List as TList, Optional, Union

from ringneck.ast.base import Node, Visitor, VisitorType
from ..tokens import Token


class ExpressionVisitor(Visitor[VisitorType]):
    ...


@dataclass
class Expression(Node):
    ...


@dataclass
class ExpressionList(Expression):
    expressions: TList['Expression']


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
    operator: Token
    value: Any


@dataclass
class MultiAssign(Expression):
    identifiers: Union['Tuple', 'List']
    operator: Token
    values: Union['Tuple', 'List']


@dataclass
class AssignIterator(Expression):
    iterator: VariableIterator
    operator: Token
    value: Any


@dataclass
class Starred(Expression):
    operator: Token
    value: Any


@dataclass
class KeyDatum(Expression):
    key: Expression
    datum: Expression


@dataclass
class Dict(Expression):
    values: TList[KeyDatum]


@dataclass
class Tuple(Expression):
    values: TList[Expression] | ExpressionList | Starred


@dataclass
class List(Expression):
    values: TList[Expression] | ExpressionList | Starred


@dataclass
class Call(Expression):
    callee: Expression
    paren: Token
    arguments: Optional[ExpressionList]


@dataclass
class Conditional(Expression):
    left: Expression
    condition: Expression
    right: Expression


@dataclass
class IteratorValue(Expression):
    token: Token
