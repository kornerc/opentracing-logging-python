
from opentracing import logs

default_format = {
    logs.EVENT: '%(levelname_lower)s',
    logs.MESSAGE: '%(message)s',
}
