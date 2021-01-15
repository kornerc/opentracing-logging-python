import logging
import time

from jaeger_client import Config

from logging_opentracing import OpenTracingHandler

# initialize a jaeger tracer
tracer = Config(
    service_name='logging_opentracing',
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
        'reporter_batch_size': 1,
    }
).initialize_tracer()

# prepare the logger
logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)
# create a new OpenTracing handler
handler = OpenTracingHandler(tracer=tracer)
logger.addHandler(handler)

# start an active span
with tracer.start_active_span('hello-world') as scope:
    # this log will be propagated to
    logger.info('Hello World from Python logging to OpenTracing')

# give Jaeger some time to send all the data
time.sleep(2)
