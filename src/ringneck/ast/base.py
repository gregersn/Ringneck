from dataclasses import dataclass
from typing import Any, Generic, Mapping, MutableMapping, Optional, TypeVar


VisitorType = TypeVar('VisitorType')


class UnknownNodeType(Exception):
    """Unknown node type."""


class Visitor(Generic[VisitorType]):
    """Visitor base class."""

    state: MutableMapping[str, Any]
    builtins: Mapping[str, Any]

    def __init__(self, state: Optional[MutableMapping[str, Any]] = None):
        self.state = state or {}

    def visit_generic(self, node: 'Node'):
        """Visit a generic node."""
        raise UnknownNodeType(f"No visit_{type(node).__name__} method")


@dataclass
class Node:
    """Node base class."""

    def accept(self, visitor: Visitor[Any]):
        """Accept visitor."""
        method_name = 'visit_' + \
            type(self).__name__ + '_' + type(self).__bases__[0].__name__
        visitor_function = getattr(visitor, method_name)
        return visitor_function(self)

    def __repr__(self):
        return f"<{self.__class__.__name__} />"
