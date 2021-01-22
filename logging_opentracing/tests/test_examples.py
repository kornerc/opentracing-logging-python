"""
Test the examples
"""

import pytest


def test_simple(capsys):
    from ..examples import simple

    captured = capsys.readouterr()

    assert captured.out == "{'event': 'INFO', 'message': 'Hello World from Python logging to OpenTracing'}\n"
