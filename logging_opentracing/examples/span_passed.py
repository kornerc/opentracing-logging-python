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

# start a span
with tracer.start_span('hello-world') as span:
    # this log will be propagated to OpenTracing
    logger.info('A span has been directly passed', extra={'span': span})

# retrieve the finished span
finished_span = tracer.finished_spans()[0]
# get the log line from
log = finished_span.logs[0]

# print the key_values of the log
print(log.key_values)

expected_output = "{'event': 'INFO', 'message': 'A span has been directly passed'}\n"
