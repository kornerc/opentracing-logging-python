"""
Test if OpenTracingHandler gets the active spans correctly
"""

from copy import deepcopy
import logging

from logging_opentracing import OpenTracingHandler

from .util import check_finished_spans, logger, tracer

TEST_LOG = {'event': 'info', 'message': 'This is a test log'}


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


def test_pass_span_custom_key(tracer):
    """
    Test is spans can be passed to the logging call under a custom key
    """
    operation_name = 'pass_span_custom_key'
    span_key = 'spamspam'

    logger_temp = logging.getLogger('PassSpanCustom')
    logger_temp.setLevel(logging.DEBUG)

    logger_temp.addHandler(OpenTracingHandler(tracer=tracer, span_key=span_key))

    with tracer.start_span(operation_name) as span:
        logger_temp.info(TEST_LOG['message'], extra={span_key: span})

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
