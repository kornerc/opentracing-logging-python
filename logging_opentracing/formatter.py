"""
A formatter which has the additional method :meth:`prepare_record` for preparing a record for such that methods like
:meth:`logging.LogRecord.formatMessage` can be called without the need of calling :meth:`logging.LogRecord.format`.
"""

from logging import Formatter, LogRecord


class OpenTracingFormatter(Formatter):
    def prepare_record(self, record: LogRecord):
        """
        Prepare the record for formatting

        The method :meth:`logging.LogRecord.format` prepares the record such that, for example, the function
        :meth:`logging.LogRecord.formatMessage` can be used. However, it has the overhead that it automatically
        generates a log. This method makes the same preparations without the additional overhead.
        """
        # this is part of the code from logging.LogRecord.format without generating the formatted string
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
