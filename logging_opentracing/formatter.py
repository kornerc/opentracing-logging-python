"""
A formatter which has the additional method :meth:`prepare_record` for preparing a record for such that methods like
:meth:`logging.LogRecord.formatMessage` can be called without the need of calling :meth:`logging.LogRecord.format`.
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
    @abstractmethod
    def format(self, record: LogRecord) -> Dict[str, str]:
        pass

    @property
    @abstractmethod
    def has_exception(self) -> bool:
        pass


class OpenTracingFormatter(OpenTracingFormatterABC):
    def __init__(self, kv_format: Optional[Dict[str, str]] = None, date_format: Optional[str] = None):

        if kv_format is None:
            kv_format = default_format

        self._date_format = date_format
        self._formatters = self._create_formatters(kv_format=kv_format)
        self._uses_time = any([f.usesTime() for f in self._formatters.values()])
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
        exc_info = record.exc_info
        if record.exc_info:
            self._has_exception = True

            exc_type, exc_val, exc_tb = exc_info

            # catch the output of print_tb()
            sio = StringIO()
            traceback.print_tb(exc_tb, file=sio)
            exc_tb = sio.getvalue()
            sio.close()

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

        if len(self._formatters) == 0:
            return dict()

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
