import logging
import re
import sys

from opentracing.mocktracer import MockTracer

from logging_opentracing import OpenTracingHandler

# initialize a mock tracer
tracer = MockTracer()

# prepare the logger
logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)

# create a new OpenTracing handler for the logging package
handler = OpenTracingHandler(tracer=tracer)
logger.addHandler(handler)

# start an active span
with tracer.start_active_span('hello-world'):
    try:
        logger.info('This will be difficult')
        # this statement will cause a ZeroDivisionError
        1 / 0
    except ZeroDivisionError:
        logger.exception('Oh no we have a ZeroDivision Error')

# retrieve the finished span
finished_span = tracer.finished_spans()[0]

print(finished_span.logs[0].key_values)
print(finished_span.logs[1].key_values)
expected_output = "{'event': 'info', 'message': 'This will be difficult'}\n" \
                  "{'event': 'error', 'message': 'Oh no we have a ZeroDivision Error', " \
                  "'error.object': ZeroDivisionError('division by zero'), " \
                  "'error.kind': <class 'ZeroDivisionError'>, 'stack': '  " \
                  "File \"<path_suffix>/logging_opentracing/examples/exception.py\"" \
                  ", line 25, in <module>\\n    1 / 0\\n'}\n"

# Python <= 3.6 has instead of "ZeroDivisionError('division by zero')" an additional comma
# "ZeroDivisionError('division by zero,')"
if sys.version_info[0] == 3 and sys.version_info[1] <= 6:
    expected_output = re.sub("'division by zero'", "'division by zero',", expected_output)
