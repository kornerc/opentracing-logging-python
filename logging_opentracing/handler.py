"""
An OpenTracing handler for the Python logging package
"""

from logging import Handler, LogRecord
from typing import Dict, Optional

from opentracing import Span, Tracer, logs
from opentracing.ext import tags

from .formatter import OpenTracingFormatterABC, OpenTracingFormatter


class OpenTracingHandler(Handler):
    def __init__(self, tracer: Tracer, formatter: Optional[OpenTracingFormatterABC] = None, span_key: str = 'span'):
        """
        Initialize the logging handler for OpenTracing

        .. seealso:: https://docs.python.org/3/library/logging.html#logrecord-attributes

        :param tracer: OpenTracing tracer which is used to get the current scope and forward the logging calls to
            :func:`opentracing.span.log_kv` calls
        :param kv_format: The dictionary is used for formatting the OpenTracing logs. The keys are the keys which will
            be used for :func:`opentracing.span.log_kv`. The values are format strings as used by the python ``logging``
            module. If this argument is not set, a default formatter will be used

            For example, the a call to ``logger.warning('Hello World')``, where ``logger`` is a logging logger with an
            OpenTracingHandler which has been initialized with ``{'event': '%(levelname)s', 'message': '%(message)s'}``,
            will results in a call
            ``tracer.scope_manager.active.span.log_kv({'event': 'WARNING', 'message': 'Hello World'})``
        :param span_key: A span can be directly passed via the parameter ``extra`` to a logging call. This parameter
            specifies under which key in the ``extra`` parameter the handler will check if a span has been passed.
            When both, a span has been passed an active span is set, the span in the ``extra`` parameters has priority
            and will be used.

            E.g. if the key has been set to its default value ``'span'``, a span can be passed in the following way:

            .. code-block:: python

               with tracer.start_span('myspan') as span:
                   # this log will be propagated to
                   logger.info('A span has been directly passed', extra={'span': span})
        """
        super().__init__()

        self._tracer = tracer
        self._span_key = span_key
        self._formatter = formatter if formatter is not None else OpenTracingFormatter()

    def _get_span(self, record: LogRecord) -> Optional[Span]:
        """
        Try to get the current span.

        1. Check if the record provides a span
        2. If the span does not contain a span try to get the span with the ScopeManager

        In the case that no span can be retrieved, return ``None``.

        :param record: Logging record
        :return: Span if it was retrievable, otherwise, ``None``.
        """
        # has a Span been provided in the record
        span = getattr(record, self._span_key) if hasattr(record, self._span_key) else None

        # try to get an active span from the ScopeManager
        if span is None:
            scope = self._tracer.scope_manager.active

            # a scope must be active, otherwise the log cannot be sent to OpenTracing
            if scope is not None:
                span = scope.span

        return span

    @staticmethod
    def _on_error(span: Span, key_values: Dict[str, str], exc_type, exc_val, exc_tb):
        """
        This function will be called in the case that an exception was raised.
        It adds the exception information to the log and tries to stick to the same format opentracing is using when
        an uncaught exception is raised.
        However, it will not overwrite existing key-value pairs.
        """
        if not span or not exc_val:
            return

        span.set_tag(tags.ERROR, True)

        # this is the default error format of OpenTracing
        default_error_format = {
            logs.EVENT: tags.ERROR,
            logs.MESSAGE: str(exc_val),
            logs.ERROR_OBJECT: exc_val,
            logs.ERROR_KIND: exc_type,
            logs.STACK: exc_tb,
        }

        for k, v in default_error_format.items():
            # don't replace key-value pairs which are already present
            if k not in key_values:
                key_values[k] = v

    def emit(self, record: LogRecord):
        """
        Log the record

        :param record: Logging record
        """
        span = self._get_span(record=record)

        if span is None:
            return

        key_values = self._formatter.format(record=record)

        if self._formatter.has_exception:
            span.set_tag(tags.ERROR, True)

        # log the key-values pairs in the span
        span.log_kv(key_values)
