"""
Test general logging features
"""

import logging

from logging_opentracing import OpenTracingHandler

from .util import tracer, check_finished_spans
from .test_get_span import TEST_LOG


def test_root_logger(caplog, tracer):
    """
    Test root logger of logging
    """
    handler = OpenTracingHandler(tracer=tracer)

    caplog.set_level(level=logging.DEBUG)
    logging.root.addHandler(handler)

    operation_name = 'my_active_span'

    with tracer.start_active_span(operation_name):
        logging.info(TEST_LOG['message'])

    check_finished_spans(tracer=tracer, operation_names_expected=[operation_name],
                         logs_expected={operation_name: [TEST_LOG]})

    logging.root.removeHandler(handler)
