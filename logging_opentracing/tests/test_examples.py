"""
Test the examples
"""

import pytest
import importlib


@pytest.mark.parametrize('name,expected_out', [
    ('simple', "{'event': 'INFO', 'message': 'Hello World from Python logging to OpenTracing'}\n"),
    ('custom_formatter', "{'event': 'INFO', 'message': 'Hello World from Python logging to OpenTracing', "
                         "'source': 'custom_formatter.py:L26'}\n"),
    ('span_passed', "{'event': 'INFO', 'message': 'A span has been directly passed'}\n"),
])
def test_example(capsys, name, expected_out):
    # from ..examples import simple
    importlib.import_module(f'..examples.{name}', package='logging_opentracing.tests')

    captured = capsys.readouterr()

    assert captured.out == expected_out
