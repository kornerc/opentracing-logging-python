import logging
from typing import Dict, List

from logging_opentracing import OpenTracingHandler
from opentracing import Tracer
from opentracing.mocktracer import MockTracer
import pytest


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
        assert operation_name_expected == span.operation_name, \
            f'The expected operation name is "{operation_names_expected}", however, the operation name is ' \
            f'"{span.operation_name}"'

        logs = span.logs
        span_logs_expected = logs_expected[operation_name_expected]

        assert len(span_logs_expected) == len(logs), \
            f'For the span "{operation_names_expected}" {len(span_logs_expected)} logs are expected but {len(logs)} ' \
            f'are available'

        for log, key_values_expected in zip(logs, span_logs_expected):
            assert str(key_values_expected) == str(log.key_values), \
                f'For the span "{operation_names_expected}" a log "{key_values_expected}" is expected, however, the ' \
                f'log is "{log.key_values}"'


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

    # this fixture is called multiple times and we have to remove the handlers added from the previous fixture call
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(OpenTracingHandler(tracer=tracer))

    return logger
