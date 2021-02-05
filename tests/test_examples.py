"""
Test the examples
"""

import importlib
import pytest
import re


@pytest.mark.parametrize('name', ['simple', 'custom_formatter', 'span_passed', 'exception', 'extra_kv'])
def test_example(capsys, name):
    module = importlib.import_module(f'examples.{name}', package='logging_opentracing.tests')

    captured = capsys.readouterr()

    captured_out = captured.out
    expected_out = module.expected_output

    # in the case that we run the exception example we have to remove the absolute path from the log because
    # this will be different on every machine
    if name == 'exception':
        regex = r'File ".*exception\.py"'
        captured_out = re.sub(regex, '', captured_out)
        expected_out = re.sub(regex, '', expected_out)

    assert captured_out == expected_out
