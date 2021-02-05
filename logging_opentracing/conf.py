"""
Configuration
"""

from opentracing import logs

#: default format which is used when no format for the OpenTracingFormatter is provided
default_format = {
    logs.EVENT: '%(levelname_lower)s',
    logs.MESSAGE: '%(message)s',
}
