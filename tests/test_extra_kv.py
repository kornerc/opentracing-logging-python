"""
Test passing additional key-values via the extra parameter of logging calls
"""

import logging

from logging_opentracing import OpenTracingHandler
import pytest


from .util import check_finished_spans, tracer, logger

EXTRA_KV = {'key a': [1, 2, 3], 'key b': 'string', 'key c': True}
LOG = {**{'event': 'info', 'message': 'Log with additional key-values'},
       **{key: str(value) for key, value in EXTRA_KV.items()}}


def test_extra_kv(tracer, logger):
    """
    Test if extra key-value pairs can be passed to a logging call
    """
    operation_name = 'extra_kv'

    with tracer.start_active_span(operation_name):
        logger.info(LOG['message'], extra={'kv': EXTRA_KV, 'my dict': {'a': 1, 'b': 2}})

    check_finished_spans(tracer=tracer, operation_names_expected=[operation_name],
                         logs_expected={operation_name: [LOG]})


def test_extra_kv_custom_key(tracer):
    """
    Test if setting a custom "extra_kv_key" of a OpenTracingHandler works
    """
    operation_name = 'custom_extra_key'
    extra_kv_key = 'properties'

    logger_temp = logging.getLogger('CustomKey')
    logger_temp.setLevel(logging.DEBUG)

    logger_temp.addHandler(OpenTracingHandler(tracer=tracer, extra_kv_key=extra_kv_key))

    with tracer.start_active_span(operation_name):
        logger_temp.info(LOG['message'], extra={extra_kv_key: EXTRA_KV, 'kv': {1: 'a', 2: 'b'},
                                                'my dict': {'a': 1, 'b': 2}})

    check_finished_spans(tracer=tracer, operation_names_expected=[operation_name],
                         logs_expected={operation_name: [LOG]})


def test_extra_kv_wrong_type(tracer, logger):
    """
    Test if an exception is raised when instead of a dict a different data type is passed for the expected key-value
    pairs
    """
    with pytest.raises(TypeError):
        with tracer.start_active_span('wrong_type'):
            logger.info('Wrong type', extra={'kv': 'this should be a dict and not a string'})
