import logging

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
    # this log will be propagated to
    logger.info('Hello World from Python logging to OpenTracing')

# retrieve the finished span
finished_span = tracer.finished_spans()[0]
# get the log line from
log = finished_span.logs[0]

# print the key_values of the log
print(log.key_values)

expected_output = "{'event': 'info', 'message': 'Hello World from Python logging to OpenTracing'}\n"
