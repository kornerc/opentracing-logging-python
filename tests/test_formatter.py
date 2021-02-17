"""
Test the OpenTracingFormatter
"""

import logging

from logging_opentracing import OpenTracingHandler, OpenTracingFormatter
import pytest

from .util import check_finished_spans, tracer

MESSAGE = 'We are the knights who say "Ni!"'


@pytest.mark.parametrize('kv_format,expected', [
    (None, {'event': 'info', 'message': MESSAGE}),
    ({'event': '%(levelname)s'}, {'event': 'INFO'}),
    ({'event': '%(levelname_lower)s'}, {'event': 'info'}),
    ({'message': '%(message)s', 'foo': 'bar'}, {'message': MESSAGE, 'foo': 'bar'}),
])
def test_custom_formats(tracer, kv_format, expected):
    """
    Test custom formats of the OpenTracingFormatter
    """
    operation_name = 'custom_formatter'
    logger = logging.getLogger('CustomFormatter')
    logger.setLevel(logging.DEBUG)

    # this test is called multiple times and we have to remove the handlers added from the previous function call
    logger.handlers.clear()

    formatter = OpenTracingFormatter(kv_format=kv_format)
    logger.addHandler(OpenTracingHandler(tracer=tracer, formatter=formatter))

    with tracer.start_active_span(operation_name):
        logger.info(MESSAGE)

    check_finished_spans(tracer=tracer, operation_names_expected=[operation_name],
                         logs_expected={operation_name: [expected]})
