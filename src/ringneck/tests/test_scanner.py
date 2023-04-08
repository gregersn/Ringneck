"""Test the scanner."""
import pytest

from ringneck.scanner import Scanner
from ringneck.tests.cases import testcases


@pytest.mark.parametrize("program,result", [(case.program, case.token_count) for case in testcases if case.token_count is not None])
def test_tokenizer(program: str, result: int):
    scanner = Scanner(program)
    res = scanner.scan_tokens()
    assert len(res) == result + 1, program
