from dsmr_parser.parsers import ValueParser
from dsmr_parser.value_types import timestamp

PG_FAILURE_EVENT = r'0-0:96.7.19'

PG_HEAD_PARSERS = [ValueParser(int), ValueParser(str)]
PG_UNIDENTIFIED_BUFFERTYPE_PARSERS = [ValueParser(str), ValueParser(str)]
BUFFER_TYPES = {
    PG_FAILURE_EVENT:  [ValueParser(timestamp), ValueParser(int)]
}
