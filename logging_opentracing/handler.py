"""
An OpenTracing handler for the Python logging package
"""

from logging import Handler, LogRecord
from typing import Optional

from opentracing import Span, Tracer
from opentracing.ext import tags

from .formatter import OpenTracingFormatterABC, OpenTracingFormatter


class OpenTracingHandler(Handler):
    def __init__(self, tracer: Tracer, formatter: Optional[OpenTracingFormatterABC] = None, span_key: str = 'span',
                 extra_kv_key: str = 'kv'):
        """
        Initialize the logging handler for OpenTracing

        .. seealso:: https://docs.python.org/3/library/logging.html#logrecord-attributes

        :param tracer: OpenTracing tracer which is used to get the current scope and forward the logging calls to
            :func:`opentracing.span.log_kv` calls
        :param formatter: Formatter which will be used to format the logs. If no formatter is provided,
            :class:`OpenTracingFormatter` with its default arguments will be used.
        :param span_key: A span can be directly passed via the parameter ``extra`` to a logging call. This parameter
            specifies under which key in the ``extra`` parameter the handler will check if a span has been passed.
            When both, a span has been passed an active span is set, the span in the ``extra`` parameters has priority
            and will be used.

            E.g. if the key has been set to its default value ``'span'``, a span can be passed in the following way:

            .. code-block:: python

               with tracer.start_span('myspan') as span:
                   # this log will be propagated to
                   logger.info('A span has been directly passed', extra={'span': span})
        :param extra_kv_key: Set the key for which for additional key_value pairs can be passed to a logging call

            .. code-block:: python

                logger.info('A span has been directly passed', extra={extra_kv_key: {'key 1': 'value 1', 'key 2': 2}})
        """
        super().__init__()

        self._tracer = tracer
        self._span_key = span_key
        self._extra_kv_key = extra_kv_key
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

    def emit(self, record: LogRecord):
        """
        Log the record

        :param record: Logging record
        """
        span = self._get_span(record=record)

        if span is None:
            return

        key_values = self._formatter.format(record=record)

        # in the case of an exception, add an error tag of the span
        if record.exc_info:
            span.set_tag(tags.ERROR, True)

        # check if a key-value pair with the key self._extra_kv_key has been passed to the extra parameter of a logging
        # call
        if hasattr(record, self._extra_kv_key):
            key_values_extra = getattr(record, self._extra_kv_key)

            if not isinstance(key_values_extra, dict):
                raise TypeError(f'A dict is expected when passing a key-value pair with the key "{self._extra_kv_key}"'
                                f' to the "extra" parameter of a logging call')

            # convert the values to strings and update the key-value pairs
            key_values.update(key_values_extra)

        # log the key-values pairs in the span
        span.log_kv(key_values)
