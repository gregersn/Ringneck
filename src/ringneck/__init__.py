from typing import Any
from ringneck.error_handler import ErrorHandler
from ringneck.interpreter import Interpreter
from ringneck.parser import Parser

from ringneck.scanner import Scanner


def run(program: str, *, global_variables: Any = None, builtins: Any = None):
    ErrorHandler.reset()
    scanner = Scanner(program)
    tokens = scanner.scan_tokens()

    parser = Parser(tokens)
    tree = parser.parse()

    if ErrorHandler.errors:
        return

    interpreter = Interpreter(
        global_variables=global_variables,
        builtins=builtins)
    return interpreter.interpret(tree)
