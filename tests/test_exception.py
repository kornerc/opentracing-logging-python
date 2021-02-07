"""
Test passing exceptions to logs
"""

import inspect

import pytest

from .util import check_finished_spans, logger, tracer


@pytest.mark.parametrize('stmt,exception', [
    ('1 / 0', ZeroDivisionError('division by zero')),
    ('y = non_existent_variable', NameError("name 'non_existent_variable' is not defined")),
    ('import non_existent_package', ModuleNotFoundError("No module named 'non_existent_package'")),
])
def test_exception(logger, tracer, stmt, exception):
    operation_name = 'span_exception'
    log = {
              'event': 'error',
              'message': 'Who would cross the Bridge of Death must answer me these questions three, '
                         'ere the other side he see.',
              'error.object': exception,
              'error.kind': exception.__class__,
              'stack': f'  File "{__file__}", line ' + '{lineno}, in {func}\n    exec(stmt)\n  File "<string>", '
                                                       'line 1, in <module>\n',
    }

    with tracer.start_active_span(operation_name):
        try:
            lineno = inspect.currentframe().f_lineno + 1
            exec(stmt)
        except exception.__class__:
            func = inspect.currentframe().f_code.co_name
            log['stack'] = log['stack'].format(lineno=lineno, func=func)

            logger.exception(log['message'])

    check_finished_spans(tracer=tracer, operation_names_expected=[operation_name],
                         logs_expected={operation_name: [log]})

