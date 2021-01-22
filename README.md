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

Here some explanation

```python
# initialize a mock tracer
tracer = MockTracer()
```
Initialize the mock tracer from the OpenTracing library.
As mentioned before, instead you can use any OpenTracing compatible tracer.

```python
# prepare the logger
logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)
```
Prepare a logger from the Python `logging` package.
Set its logging level to `INFO` such that logs with the severity `INFO` are also captured.

```python
# create a new OpenTracing handler for the logging package
handler = OpenTracingHandler(tracer=tracer)
logger.addHandler(handler)
```
First, initialize the OpenTracing handler `OpenTracingHandler` for `logging`.
It needs an OpenTracing tracer as parameter.
Then, add the handler to the logger.

```python
# start an active span
with tracer.start_active_span('hello-world') as scope:
    # this log will be propagated to
    logger.info('Hello World from Python logging to OpenTracing')
```
Start a new active span with the name `hello-world`.
Within this active span, make a log with the severity info.
It is expected that this log will be captured by our handler for OpenTracing which should forward the log to our tracer.

```python
# retrieve the finished span
finished_span = tracer.finished_spans()[0]
# get the log line from
log = finished_span.logs[0]

# print the key_values of the log
# expected output: {'event': 'INFO', 'message': 'Hello World from Python logging to OpenTracing'}
print(log.key_values)
```
These lines are only used to check if the log have been successfully forwarder to out tracer.

### Custom Formatter

TODO
