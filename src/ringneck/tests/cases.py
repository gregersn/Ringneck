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
    globals: Optional[Dict[str, Any]] = None


testcases: Sequence[TestCase] = [
    TestCase('', 0, []),
    TestCase('\n', 0, []),
    TestCase('6', 1, ['6'], [6]),
    TestCase('5.25', 1, ['5.25'], [5.25]),
    TestCase('1 + 2', 3, ['(+ 1 2)'], [3]),
    TestCase('1 - 2', 3, ['(- 1 2)'], [-1]),
    TestCase('6 / 3', 3, ['(/ 6 3)'], [2]),
    TestCase('3 * 2', 3, ['(* 3 2)'], [6]),
    TestCase('1 + (2 + 3)', 7, ['(+ 1 (grouping (+ 2 3)))']),
    TestCase('1 == 1', 3, ['(== 1 1)'], [True]),
    TestCase('1 + None', 3, ['(+ 1 None)']),
    TestCase('a = 1', 3, ['(assign a 1)'], [None], state={'a': 1}),
    TestCase('a = []', 4, ['(assign a (list ))'], state={'a': []}),
    TestCase('a = (1, 2, 3)', 9, [
             '(assign a (tuple 1, 2, 3))'], state={'a': (1, 2, 3)}),
    TestCase('a = 1, 2, 3', 7, [
             '(assign a (tuple 1, 2, 3))'], state={'a': (1, 2, 3)}),
    TestCase('a = [1, 2, 3]', 9, ['(assign a (list 1, 2, 3))']),
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
    TestCase(""""""),
    TestCase("a = 5 < 4\nb = 5 < 5\nc = 5 < 6", state={
             'a': False, 'b': False, 'c': True}),
    TestCase("a = 5 <= 4\nb = 5 <= 5\nc = 5 <= 6", state={
             'a': False, 'b': True, 'c': True}),
    TestCase("a = 5 > 4\nb = 5 > 5\nc = 5 > 6", state={
             'a': True, 'b': False, 'c': False}),
    TestCase("a = 5 >= 4\nb = 5 >= 5\nc = 5 >= 6", state={
             'a': True, 'b': True, 'c': False}),
    TestCase("$.HP = ($.DEX + $.STR) / 10 + 1", 11),
    TestCase("a = 7 if 1 < 2 else 9", 9, [
             '(assign a (if 7 (< 1 2) 9))'], state={'a': 7}),
    TestCase("a = 7 if 2 < 1 else 9", 9, state={'a': 9}),
    TestCase("1 and 2", 3, ['(and 1 2)'], [2]),
    TestCase('a = 1\nb ?= 2\na ?= 3', 11, state={'a': 1, 'b': 2}),
    TestCase('a = foo(bar, b) + baz(zoo, c)', 15,
             ['(assign a (+ (call foo bar b) (call baz zoo c)))']),
    TestCase('$.a = foo_ooo(ba_ar, $.c) + some_function(a_name, $.d)', 15,
             ['(assign $.a (+ (call foo_ooo ba_ar $.c) (call some_function a_name $.d)))']),
    TestCase("""a = 1
# comment
b = 2
""", 8, ["(assign a 1)", "(assign b 2)"]),
    TestCase("a, b = 1, 2", 7, [
             "(assign (tuple a, b) (tuple 1, 2))"], state={'a': 1, 'b': 2}),
    TestCase("a=[*(1, 2, 3)]", 12,
             ["(assign a (starred (tuple 1, 2, 3)))"], state={'a': [1, 2, 3]}),
    TestCase("$.['a', 'b', 'c'] = %", 10, globals={
             'a': 'a', 'b': 'b', 'c': 'c'}),
    TestCase("a=(1, 2)\nb, c = a", 13, [
             "(assign a (tuple 1, 2))", "(assign (tuple b, c) a)"], state={'a': (1, 2), 'b': 1, 'c': 2}),
    TestCase("a=1\na-=1", 7, ["(assign a 1)",
             "(-= a 1)"], state={'a': 0}),
    TestCase("""a=1
if a > 0:
b = 2
endif
if a > 4:
a=6
endif
if b < 3 and a < 5:
a=0
c=3
endif""", 47,
             ["(assign a 1)", "(if (> a 0) (assign b 2))", "(if (> a 4) (assign a 6))",
              "(if (and (< b 3) (< a 5)) (assign a 0) (assign c 3))"],
             state={'a': 0, 'b': 2, 'c': 3}),
    TestCase("a=0\nrepeat a += 1 times 5", 10,
             ["(assign a 0)", "(repeat 5 (+= a 1))"], state={'a': 5}),
    TestCase("a=foo(*bar.baz)", 7, ["(assign a (call foo (starred bar.baz)))"])

]
