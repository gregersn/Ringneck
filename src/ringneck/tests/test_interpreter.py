"""Test miscellanous Troll rolls."""
from typing import Any, Dict, List

import pytest

from ringneck.interpreter import Interpreter
from ringneck.parser import Parser
from ringneck.scanner import Scanner

from ringneck.tests.cases import testcases


@pytest.mark.parametrize("program,result", [(case.program, case.interpret_result) for case in testcases if case.interpret_result is not None])
def test_interpret(program: str, result: List[Any]):
    scanner = Scanner(program)
    parser = Parser(scanner.scan_tokens())
    expression = parser.parse()

    interpreter = Interpreter()
    res = interpreter.interpret(expression)
    assert res == result, program


@pytest.mark.parametrize("program,state", [(case.program, case.state) for case in testcases if case.state is not None])
def test_interpreter_state(program: str, state: Dict[str, Any]):
    scanner = Scanner(program)
    parser = Parser(scanner.scan_tokens())
    expression = parser.parse()

    interpreter = Interpreter()
    interpreter.interpret(expression)
    assert interpreter.state == state


@pytest.mark.parametrize("program,globals", [(case.program, case.globals) for case in testcases if case.globals is not None])
def test_interpreter_globals(program: str, globals: Dict[str, Any]):
    scanner = Scanner(program)
    parser = Parser(scanner.scan_tokens())
    expression = parser.parse()

    interpreter = Interpreter()
    interpreter.interpret(expression)
    assert interpreter.globals == globals
