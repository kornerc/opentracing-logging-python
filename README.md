# opentracing-logging-python
OpenTracing handler for the Python logging library

**Warning: This library is currently in an alpha state**

## Installation

TODO

## Usage
We use Jaeger for the follwing examples but you can also use other OpenTracing compatible tracers.
For preparation download the [jaeger-all-in-one executable](https://www.jaegertracing.io/download/#binaries), unpack,
and start it.

```batch
jaeger-all-in-one.exe --collector.zipkin.http-port=9411
```

### Simple
```python
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
```

Navigate with your webbrowser to <http://localhost:16686>.
You should see the trace with the log line.

### Custom Formatter

TODO
