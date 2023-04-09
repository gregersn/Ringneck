"""Test cases."""
from dataclasses import dataclass
from typing import Any, Dict, Sequence, Optional


@dataclass
class TestCase:
    program: str
    token_count: Optional[int] = None
    parse_result: Optional[Sequence[str]] = None
    interpret_result: Optional[Sequence[Any]] = None
    error: Optional[str] = None
    state: Optional[Dict[str, Any]] = None


testcases: Sequence[TestCase] = [
    TestCase('', 0, []),
    TestCase('\n', 0, []),
    TestCase('6', 1, ['6'], [6]),
    TestCase('1 + 2', 3, ['(+ 1 2)'], [3]),
    TestCase('1 + (2 + 3)', 7, ['(+ 1 (grouping (+ 2 3)))']),
    TestCase('a = 1', 3, ['(assign a 1)'], [None], state={'a': 1}),
    TestCase('a = {"foo": "bar"}', 7, [
             '(assign a (dict foo: bar))'], state={'a': {'foo': 'bar'}}),
    TestCase('$.foo = 3', 3, ['(assign $.foo 3)'], [None]),
    TestCase('a = [1, 2]', 7, ['(assign a (list 1, 2))']),
    TestCase('a={"x": 1, "y": 2, "z": 3}\na.["x", "y"] = 3', 24,
             ['(assign a (dict x: 1, y: 2, z: 3))',
              '(assign a.(list x, y) 3)'],
             state={'a': {'x': 3, 'y': 3, 'z': 3}}),
    TestCase("""kin = {
    1: Human
    2: Elf
}""", 13, ['(assign kin (dict 1: Human, 2: Elf))']),
]
