import logging
import time

from opentracing.mocktracer import MockTracer

from logging_opentracing import OpenTracingHandler

# initialize a mock tracer
tracer = MockTracer()

# prepare the logger
logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)

# create a new OpenTracing handler for the logging package and use own format
handler = OpenTracingHandler(tracer=tracer, kv_format={
    'event': '%(levelname)s',
    'message': '%(message)s',
    'source': '%(filename)s:L%(lineno)d',
})
logger.addHandler(handler)

# start an active span
with tracer.start_active_span('hello-world') as scope:
    # this log will be propagated to
    logger.info('Hello World from Python logging to OpenTracing')

# retrieve the finished span
finished_span = tracer.finished_spans()[0]
# get the log line from
log = finished_span.logs[0]

# print the key_values of the log
# expected output: {'event': 'INFO', 'message': 'Hello World from Python logging to OpenTracing', 'source': 'custom_formatter.py:L26'}
print(log.key_values)
