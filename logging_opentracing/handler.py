from logging import Handler, LogRecord, Formatter
from typing import Dict, Optional

from opentracing import Span, Tracer


class OpenTracingHandler(Handler):
    #: Default formatter which is used when no `kv_format` has been specified in the constructor
    default_formatter = {
        'event': '%(levelname)s',
        'message': '%(message)s',
    }

    def __init__(self, tracer: Tracer, kv_format: Optional[Dict[str, str]] = None, span_key: str = 'span'):
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

        if kv_format is None:
            kv_format = self.default_formatter

        self._tracer = tracer
        self._span_key = span_key
        self._formatters = self._create_formatters(kv_format=kv_format)

    def _create_formatters(self, kv_format: Dict[str, str]) -> Dict[str, Formatter]:
        """
        Initialize the formatters
        """
        return {key: Formatter(fmt=fmt) for key, fmt in kv_format.items()}

    def _format_kv(self, record: LogRecord) -> Dict[str, str]:
        return {key: formatter.format(record) for key, formatter in self._formatters.items()}

    def _get_span(self, record: LogRecord) -> Optional[Span]:
        span = getattr(record, self._span_key) if hasattr(record, self._span_key) else None

        if span is None:
            scope = self._tracer.scope_manager.active

            # a scope must be active, otherwise the log cannot be sent to OpenTracing
            if scope is not None:
                span = scope.span

        return span

    def emit(self, record: LogRecord):
        span = self._get_span(record=record)

        if span is None:
            return

        span.log_kv(self._format_kv(record=record))
