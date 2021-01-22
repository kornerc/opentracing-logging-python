# opentracing-logging-python
OpenTracing handler for the Python logging library

**Warning: This library is currently in an alpha state**

## Installation

TODO

## Usage
We use the mock tracer for the follwing examples but you can also use other OpenTracing compatible tracers.

An compatible tracer would be, for instance, [Jaeger](https://github.com/jaegertracing/jaeger-client-python)

### Simple
In the first example we initialize the `OpenTracingHandler` for `logging` and create an active span with the name
`hello-world`.
In this active span we make make an info-log and in the end we have a look if this log was forwarded to OpenTracing.

```python
import logging
import time

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
    # this log will be propagated to
    logger.info('Hello World from Python logging to OpenTracing')

# retrieve the finished span
finished_span = tracer.finished_spans()[0]
# get the log line from
log = finished_span.logs[0]

# print the key_values of the log
# expected output: {'event': 'INFO', 'message': 'Hello World from Python logging to OpenTracing'}
print(log.key_values)
```

### Custom Formatter

TODO
