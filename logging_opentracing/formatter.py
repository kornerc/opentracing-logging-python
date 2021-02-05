"""
Formatter to provide logs in a Python dictionary format which can be used by the OpenTracingHandler
"""

from abc import ABC, abstractmethod
from io import StringIO
from logging import Formatter, LogRecord
import traceback
from typing import Dict, Optional

from opentracing import logs
from opentracing.ext import tags

from .conf import default_format


class OpenTracingFormatterABC(ABC):
    """
    Abstract class which is used to define the methods which are used by :class:`OpenTracingHandler`.
    This package uses the class :class:`OpenTracingFormatter` to implement this abstract class but it is possible to
    use other implementations
    """

    @abstractmethod
    def format(self, record: LogRecord) -> Dict[str, str]:
        """
        Format a record in a dictionary format.

        :param record: Record to be formatted
        :return: Log in a key-value format in a dictionary.
        """
        pass

    @property
    @abstractmethod
    def has_exception(self) -> bool:
        """
        Check if the last record which has been passed to the method :meth:`format` contained an exception.

        :return: `True` when the last record had an exception attached, `False` otherwise.
        """
        pass


class OpenTracingFormatter(OpenTracingFormatterABC):
    """
    Formatter to prepare key-value pairs for OpenTracing logging
    """

    def __init__(self, kv_format: Optional[Dict[str, str]] = None, date_format: Optional[str] = None):
        """
        Prepare and define the format which should be used for the OpenTracing logs

        :param kv_format: The dictionary is used for formatting the OpenTracing logs. The keys are the keys which will
            be used for :func:`opentracing.span.log_kv`. The values are format strings as used by the python ``logging``
            module. If this argument is not set, a default formatter will be used

            For example, the a call to ``logger.warning('Hello World')``, where ``logger`` is a logging logger with an
            OpenTracingHandler with an OpenTracingFormatter which has been initialized with
            ``kv_format={'event': '%(levelname_lower)s', 'message': '%(message)s'}``, will results in a call
            ``tracer.scope_manager.active.span.log_kv({'event': 'warning', 'message': 'Hello World'})``
        :param date_format: Date format which should be used. This parameter will be propagated to the parameter
            ``datefmt`` of :meth:`logging.Formatter`.
        """
        # use the default format if no format has been provided
        if kv_format is None:
            kv_format = default_format

        #: Date format to be used in the logs
        self._date_format = date_format
        #: Key-value pairs for formatting.
        #: Keys are the keys which will be used in the logs and the values are the formatters which are used to format
        #: the corresponding values in the logs.
        self._formatters = self._create_formatters(kv_format=kv_format)
        #: Is one of the formatters using time?
        self._uses_time = any([f.usesTime() for f in self._formatters.values()])
        #: Was an exception attached to the last record which has been used with the method :meth:`format`?
        self._has_exception = False

    def _create_formatters(self, kv_format: Dict[str, str]) -> Dict[str, Formatter]:
        """
        Initialize the formatters
        """
        return {key: Formatter(fmt=fmt, validate=False, datefmt=self._date_format) for key, fmt in kv_format.items()}

    def _format_message(self, record: LogRecord) -> Dict[str, str]:
        """
        Use the formatters ``self.formatters`` to format the key-value pairs for the log.

        :param record: Logging record
        :return: A dictionary containing the key-value pairs for the log
        """
        return {key: formatter.formatMessage(record=record) for key, formatter in self._formatters.items()}

    def _format_exception(self, record: LogRecord) -> Dict[str, str]:
        """
        Format an exception OpenTracing uses when formatting uncaught exceptions
        """
        exc_info = record.exc_info
        # is an exception attached to the log
        if record.exc_info:
            self._has_exception = True

            exc_type, exc_val, exc_tb = exc_info

            # catch the output of print_tb()
            sio = StringIO()
            traceback.print_tb(exc_tb, file=sio)
            exc_tb = sio.getvalue()
            sio.close()

            # format which is also used by OpenTracing
            return {
                logs.EVENT: tags.ERROR,
                logs.MESSAGE: str(exc_val),
                logs.ERROR_OBJECT: exc_val,
                logs.ERROR_KIND: exc_type,
                logs.STACK: exc_tb,
            }
        else:
            self._has_exception = False

            return dict()

    def format(self, record: LogRecord) -> Dict[str, str]:
        record.message = record.getMessage()
        record.levelname_lower = record.levelname.lower()

        # in the case that no formatter have been provided return an empty dictionary
        if len(self._formatters) == 0:
            return dict()

        # use one of the formatter to set some attribute in the record
        formatter = self._formatters[list(self._formatters.keys())[0]]

        if self._uses_time:
            record.asctime = formatter.formatTime(record=record)
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = formatter.formatException(record.exc_info)

        key_values_message = self._format_message(record=record)
        key_values_exception = self._format_exception(record=record)

        # merge the key-values of the message and the exception such that the message key-values overwrite the
        # exception key-values incase of duplicates
        return {**key_values_exception, **key_values_message}

    @property
    def has_exception(self) -> bool:
        return self._has_exception
