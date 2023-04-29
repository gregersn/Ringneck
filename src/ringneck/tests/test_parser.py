import pytest
from typing import List

from ringneck.ast.printer import ASTPrinter
from ringneck.error_handler import ErrorHandler

from ringneck.tests.cases import testcases
from ringneck.scanner import Scanner
from ringneck.parser import Parser


@pytest.mark.parametrize("program,result", [(case.program, case.parse_result) for case in testcases if case.parse_result is not None])
def test_parse(program: str, result: List[str]):
    scanner = Scanner(program)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    expression = parser.parse()
    res = ASTPrinter().print(expression)
    assert not ErrorHandler.errors, ErrorHandler.errors
    assert res == result, program
