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
with tracer.start_active_span('hello-world') as scope:
    # add additional key-value pairs to the log by providing a dict to the key "kv" of the "extra" parameter
    logger.info('Here we pass additional arguments to the log', extra={'kv': {'key a': [1, 2, 3], 'key b': 'foo'}})

# retrieve the finished span
finished_span = tracer.finished_spans()[0]
# get the log line from
log = finished_span.logs[0]

# print the key_values of the log
print(log.key_values)

expected_output = "{'event': 'info', 'message': 'Here we pass additional arguments to the log', 'key a': " \
                  "'[1, 2, 3]', 'key b': 'foo'}\n"
