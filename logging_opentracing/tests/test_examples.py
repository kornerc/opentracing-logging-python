"""
Test the examples
"""

import pytest


def test_simple(capsys):
    from ..examples import simple

    captured = capsys.readouterr()

    assert captured.out == "{'event': 'INFO', 'message': 'Hello World from Python logging to OpenTracing'}\n"


def test_custom_formatter(capsys):
    from ..examples import custom_formatter

    captured = capsys.readouterr()

    assert captured.out == "{'event': 'INFO', 'message': 'Hello World from Python logging to OpenTracing', 'source': 'custom_formatter.py:L26'}\n"
