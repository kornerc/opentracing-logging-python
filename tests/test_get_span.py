"""
Test if OpenTracingHandler gets the active spans correctly
"""

from copy import deepcopy
import logging
from typing import Dict, List

import pytest
from opentracing import Tracer
from opentracing.mocktracer import MockTracer

from logging_opentracing import OpenTracingHandler

TEST_LOG = {'event': 'info', 'message': 'This is a test log'}


@pytest.fixture
def tracer() -> Tracer:
    """
    Get a MockTracer
    """
    return MockTracer()


@pytest.fixture
def logger(tracer):
    """
    Get a logger with an initialized OpenTracingHandler
    """
    logger = logging.getLogger('Test')
    logger.setLevel(logging.DEBUG)

    # this fixture is called mutliple times and we have to remove the handlers added from the previous fixture call
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(OpenTracingHandler(tracer=tracer))

    return logger


def check_finished_spans(tracer: MockTracer, operation_names_expected: List[str],
                         logs_expected: Dict[str, List[Dict[str, str]]]):
    """
    Helper function to check if the finished spans of the tracer are as expected and the logs have also been passed
    correctly

    :param tracer: Instance of the MockTracer
    :param operation_names_expected: The operation names of the spans which are order in the same order as they have
        been created
    :param logs_expected: Expected logs for each ``operation_names_expected``. The keys of the outer dictionary are the
        names defined in ``operation_names``. For each operation name a list of logs must be provided which ordered
        correctly.
    """
    finished_spans = tracer.finished_spans()

    assert len(operation_names_expected) == len(finished_spans), \
        f'{len(operation_names_expected)} finished spans are expected but only {len(finished_spans)} have ' \
        f'been registred'

    # internally the the Mock tracer saves the traces in veversed order
    operation_names_expected.reverse()

    for span, operation_name_expected in zip(finished_spans, operation_names_expected):
        last_start_time = span.start_time

        assert operation_name_expected == span.operation_name, \
            f'The expected operation name is "{operation_names_expected}", however, the operation name is ' \
            f'"{span.operation_name}"'

        logs = span.logs
        span_logs_expected = logs_expected[operation_name_expected]

        assert len(span_logs_expected) == len(logs), \
            f'For the span "{operation_names_expected}" {len(span_logs_expected)} logs are expected but {len(logs)} ' \
            f'are available'

        for log, key_values_expected in zip(logs, span_logs_expected):
            assert key_values_expected == log.key_values, \
                f'For the span "{operation_names_expected}" a log "{key_values_expected}" is expected, however, the ' \
                f'log is "{log.key_values}"'


def test_active_span(tracer, logger):
    """
    Test if the handler can automatically retrieve an active span
    """
    operation_name = 'my_active_span'

    with tracer.start_active_span(operation_name) as scope:
        logger.info(TEST_LOG['message'])

    check_finished_spans(tracer=tracer, operation_names_expected=[operation_name],
                         logs_expected={operation_name: [TEST_LOG]})


def test_multiple_logs(tracer, logger):
    """
    Test if multiple logs are stored correctly
    """
    operation_name = 'my_active_span'

    test_log_0 = deepcopy(TEST_LOG)
    test_log_0['message'] += '_0'
    test_log_1 = deepcopy(TEST_LOG)
    test_log_1['message'] += '_1'

    with tracer.start_active_span(operation_name) as scope:
        logger.info(test_log_0['message'])
        logger.info(test_log_1['message'])

    check_finished_spans(tracer=tracer, operation_names_expected=[operation_name],
                         logs_expected={operation_name: [test_log_0, test_log_1]})


def test_no_active_span(tracer, logger):
    """
    Test logging when neither an active span is available nor a span has been passed
    """
    logger.info(TEST_LOG['message'])

    check_finished_spans(tracer=tracer, operation_names_expected=list(), logs_expected=dict())


def test_span(tracer, logger):
    """
    Test behavior when logging inside a "normal" span (not active) without passing a span
    """
    operation_name = 'my_span'

    with tracer.start_span(operation_name):
        logger.info(TEST_LOG['message'])

    check_finished_spans(tracer=tracer, operation_names_expected=[operation_name],
                         logs_expected={operation_name: list()})


def test_pass_span(tracer, logger):
    """
    Test is spans can be passed to the logging call correctly
    """
    operation_name = 'my_span_to_pass'

    with tracer.start_span(operation_name) as span:
        logger.info(TEST_LOG['message'], extra={'span': span})

    check_finished_spans(tracer=tracer, operation_names_expected=[operation_name],
                         logs_expected={operation_name: [TEST_LOG]})


def test_nested_active_span(tracer, logger):
    """
    Test if nested active spans work
    """
    operation_names = ['my_active_span_0', 'my_active_span_1']

    test_log_0 = deepcopy(TEST_LOG)
    test_log_0['message'] += '_0'
    test_log_1 = deepcopy(TEST_LOG)
    test_log_1['message'] += '_1'
    test_log_2 = deepcopy(TEST_LOG)
    test_log_2['message'] += '_2'

    with tracer.start_active_span(operation_names[0]):
        logger.info(test_log_0['message'])

        with tracer.start_active_span(operation_names[1]):
            logger.info(test_log_1['message'])

        logger.info(test_log_2['message'])

    check_finished_spans(tracer=tracer, operation_names_expected=operation_names,
                         logs_expected={operation_names[0]: [test_log_0, test_log_2], operation_names[1]: [test_log_1]})
