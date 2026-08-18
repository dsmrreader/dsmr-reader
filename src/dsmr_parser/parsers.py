import logging
import re

from ctypes import c_ushort
from decimal import Decimal

# @TODO: Disabled in DSMR-reader due to incompatibilities with dlms-cosem's dependency of "cryptography", causing:
# @TODO: "ImportError: libffi.so.7: cannot open shared object file: No such file or directory"
# @TODO: Also unused: none of DSMR-reader's own telegram specifications set "general_global_cipher",
# @TODO: and datalogger.py never calls parser.parse() with encryption/authentication keys.
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from dlms_cosem.connection import XDlmsApduFactory
# from dlms_cosem.exceptions import DecryptionError as DlmsDecryptionError
# from dlms_cosem.protocol.xdlms import GeneralGlobalCipher

from dsmr_parser.objects import MBusObject, MBusObjectPeak, CosemObject, ProfileGenericObject, Telegram
from dsmr_parser.exceptions import ParseError, InvalidChecksumError
from dsmr_parser.value_types import timestamp

logger = logging.getLogger(__name__)


class TelegramParser(object):
    crc16_tab: list[int] = []

    def __init__(self, telegram_specification, apply_checksum_validation=True):
        """
        :param telegram_specification: determines how the telegram is parsed
        :param apply_checksum_validation: validate checksum if applicable for
            telegram DSMR version (v4 and up).
        :type telegram_specification: dict
        """
        self.apply_checksum_validation = apply_checksum_validation
        self.telegram_specification = telegram_specification
        # Regexes are compiled once to improve performance
        self.telegram_specification_regexes = {
            object["obis_reference"]: re.compile(object["obis_reference"], re.DOTALL | re.MULTILINE)
            for object in self.telegram_specification['objects']
        }

    def parse(self, telegram_data, encryption_key="", authentication_key="", throw_ex=False):  # noqa: C901
        """
        Parse telegram from string to dict.
        The telegram str type makes python 2.x integration easier.

        :param str telegram_data: full telegram from start ('/') to checksum
            ('!ABCD') including line endings in between the telegram's lines
        :param str encryption_key: encryption key
        :param str authentication_key: authentication key
        :rtype: Telegram
        :raises ParseError:
        :raises InvalidChecksumError:
        """

        # @TODO: Disabled in DSMR-reader (see the @TODO above the crypto imports): general_global_cipher
        # @TODO: handling (encrypted DLMS APDU telegrams) requires dlms-cosem/cryptography, which are not
        # @TODO: installed here. None of DSMR-reader's own telegram specifications set this key.
        if self.telegram_specification.get("general_global_cipher"):
            raise NotImplementedError("general_global_cipher telegrams are not supported by DSMR-reader")

        if self.apply_checksum_validation and self.telegram_specification['checksum_support']:
            self.validate_checksum(telegram_data)

        telegram = Telegram()

        for object in self.telegram_specification['objects']:
            pattern = self.telegram_specification_regexes[object["obis_reference"]]
            matches = pattern.findall(telegram_data)

            # Some signatures are optional and may not be present,
            # so only parse lines that match
            for match in matches:
                try:
                    dsmr_object = object["value_parser"].parse(match)
                except ParseError:
                    logger.error(
                        "ignore line with signature {}, because parsing failed.".format(object["obis_reference"]),
                        exc_info=True
                    )
                    if throw_ex:
                        raise
                except Exception as err:
                    logger.error("Unexpected {}: {}".format(type(err), err))
                    raise
                else:
                    telegram.add(
                        obis_reference=object["obis_reference"],
                        dsmr_object=dsmr_object,
                        obis_name=object["value_name"]
                    )

        return telegram

    @staticmethod
    def validate_checksum(telegram):
        """
        :param str telegram:
        :raises ParseError:
        :raises InvalidChecksumError:
        """

        # Extract the part for which the checksum applies.
        checksum_contents = re.search(r'\/.+\!', telegram, re.DOTALL)

        # Extract the hexadecimal checksum value itself.
        # The line ending '\r\n' for the checksum line can be ignored.
        checksum_hex = re.search(r'((?<=\!)[0-9A-Z]{1,4})+', telegram)

        if not checksum_contents or not checksum_hex:
            raise ParseError(
                'Failed to perform CRC validation because the telegram is '
                'incomplete. The checksum and/or content values are missing.'
            )

        calculated_crc = TelegramParser.crc16(checksum_contents.group(0))
        expected_crc = int(checksum_hex.group(0), base=16)

        if calculated_crc != expected_crc:
            raise InvalidChecksumError(
                "Invalid telegram. The CRC checksum '{}' does not match the "
                "expected '{}'".format(
                    calculated_crc,
                    expected_crc
                )
            )

    @staticmethod
    def crc16(telegram):
        """
        Calculate the CRC16 value for the given telegram

        :param str telegram:
        """
        crcValue = 0x0000

        if len(TelegramParser.crc16_tab) == 0:
            for i in range(0, 256):
                crc = c_ushort(i).value
                for j in range(0, 8):
                    if (crc & 0x0001):
                        crc = c_ushort(crc >> 1).value ^ 0xA001
                    else:
                        crc = c_ushort(crc >> 1).value
                TelegramParser.crc16_tab.append(hex(crc))

        for c in telegram:
            d = ord(c)
            tmp = crcValue ^ d
            rotated = c_ushort(crcValue >> 8).value
            crcValue = rotated ^ int(TelegramParser.crc16_tab[(tmp & 0x00ff)], 0)

        return crcValue


class DSMRObjectParser(object):
    """
    Parses an object (can also be see as a 'line') from a telegram.
    """

    def __init__(self, *value_formats):
        self.value_formats = value_formats

    def _is_line_wellformed(self, line, values):
        # allows overriding by child class
        return (values and (len(values) == len(self.value_formats)))

    def _parse_values(self, values):
        # allows overriding by child class
        return [self.value_formats[i].parse(value)
                for i, value in enumerate(values)]

    def _parse_obis_id_code(self, line):
        """
        Get the OBIS ID code

        Example line:
        '0-2:24.2.1(200426223001S)(00246.138*m3)'

        OBIS ID code = 0-2 returned as tuple
        """
        try:
            return int(line[0]), int(line[2])
        except ValueError:
            raise ParseError("Invalid OBIS ID code for line '%s' in '%s'", line, self)

    def _parse(self, line):
        # Match value groups, but exclude the parentheses
        pattern = re.compile(r'((?<=\()[0-9a-zA-Z\.\*\-\:]{0,}(?=\)))')

        values = re.findall(pattern, line)

        if not self._is_line_wellformed(line, values):
            raise ParseError("Invalid '%s' line for '%s'", line, self)

        # Convert empty value groups to None for clarity.
        values = [None if value == '' else value for value in values]

        return self._parse_values(values)


class MBusParser(DSMRObjectParser):
    """
    Gas meter value parser.

    These are lines with a timestamp and gas meter value.

    Line format:
    'ID (TST) (Mv1*U1)'

     1   2     3   4

    1) OBIS Reduced ID-code
    2) Time Stamp (TST) of capture time of measurement value
    3) Measurement value 1 (most recent entry of buffer attribute without unit)
    4) Unit of measurement values (Unit of capture objects attribute)
    """

    def parse(self, line):
        return MBusObject(
            obis_id_code=self._parse_obis_id_code(line),
            values=self._parse(line)
        )


class MaxDemandParser(DSMRObjectParser):
    """
    Max demand history parser.

    These are lines with multiple values. Each containing 2 timestamps and a value

    Line format:
    'ID (Count) (ID) (ID) (TST) (TST) (Mv1*U1)'

     1  2  3  4  5  6  7

    1) OBIS Reduced ID-code
    2) Amount of values in the response
    3) ID of the source
    4) ^^
    5) Time Stamp (TST) of the month
    6) Time Stamp (TST) when the max demand occured
    6) Measurement value 1 (most recent entry of buffer attribute without unit)
    7) Unit of measurement values (Unit of capture objects attribute)
    """

    def parse(self, line):
        pattern = re.compile(r'((?<=\()[0-9a-zA-Z\.\*\-\:]{0,}(?=\)))')
        values = re.findall(pattern, line)

        obis_id_code = self._parse_obis_id_code(line)

        objects = []

        count = int(values[0])
        for i in range(1, count + 1):
            timestamp_month = ValueParser(timestamp).parse(values[i * 3 + 0])
            timestamp_occurred = ValueParser(timestamp).parse(values[i * 3 + 1])
            value = ValueParser(Decimal).parse(values[i * 3 + 2])
            objects.append(MBusObjectPeak(
                obis_id_code=obis_id_code,
                values=[timestamp_month, timestamp_occurred, value]
            ))

        return objects


class CosemParser(DSMRObjectParser):
    """
    Cosem object parser.

    These are data objects with a single value that optionally have a unit of
    measurement.

    Line format:
    ID (Mv*U)

    1  23  45

    1) OBIS Reduced ID-code
    2) Separator "(", ASCII 28h
    3) COSEM object attribute value
    4) Unit of measurement values (Unit of capture objects attribute) - only if
       applicable
    5) Separator ")", ASCII 29h
    """

    def parse(self, line):
        return CosemObject(
            obis_id_code=self._parse_obis_id_code(line),
            values=self._parse(line)
        )


class ProfileGenericParser(DSMRObjectParser):
    """
    Power failure log parser.

    These are data objects with multiple repeating groups of values.

    Line format:
    ID (z) (ID1) (TST) (Bv1*U1) (TST) (Bvz*Uz)

    1   2   3     4     5   6    7     8   9

    1) OBIS Reduced ID-code
    2) Number of values z (max 10).
    3) Identifications of buffer values (OBIS Reduced ID codes of capture objects attribute)
    4) Time Stamp (TST) of power failure end time
    5) Buffer value 1 (most recent entry of buffer attribute without unit)
    6) Unit of buffer values (Unit of capture objects attribute)
    7) Time Stamp (TST) of power failure end time
    8) Buffer value 2 (oldest entry of buffer attribute without unit)
    9) Unit of buffer values (Unit of capture objects attribute)
    """

    def __init__(self, buffer_types, head_parsers, parsers_for_unidentified):
        self.value_formats = head_parsers.copy()
        self.buffer_types = buffer_types
        self.parsers_for_unidentified = parsers_for_unidentified

    def _is_line_wellformed(self, line, values):
        if values and (len(values) == 1) and (values[0] == ''):
            # special case: single empty parentheses (indicated by empty string)
            return True

        if values and (len(values) >= 2) and (values[0].isdigit()):
            buffer_length = int(values[0])
            return (buffer_length <= 10) and (len(values) == (buffer_length * 2 + 2))
        else:
            return False

    def _parse_values(self, values):
        if values and (len(values) == 1) and (values[0] is None):
            # special case: single empty parentheses; make sure empty ProfileGenericObject is created
            values = [0, None]  # buffer_length=0, buffer_value_obis_ID=None
        buffer_length = int(values[0])
        buffer_value_obis_ID = values[1]
        if (buffer_length > 0):
            if buffer_value_obis_ID in self.buffer_types:
                bufferValueParsers = self.buffer_types[buffer_value_obis_ID]
            else:
                bufferValueParsers = self.parsers_for_unidentified
        # add the parsers for the encountered value type z times
        for _ in range(buffer_length):
            self.value_formats.extend(bufferValueParsers)

        return [self.value_formats[i].parse(value) for i, value in enumerate(values)]

    def parse(self, line):
        return ProfileGenericObject(
            obis_id_code=self._parse_obis_id_code(line),
            values=self._parse(line)
        )


class ValueParser(object):
    """
    Parses a single value from DSMRObject's.

    Example with coerce_type being int:
        (002*A) becomes {'value': 2, 'unit': 'A'}

    Example with coerce_type being str:
        (42) becomes {'value': '42', 'unit': None}
    """

    def __init__(self, coerce_type):
        self.coerce_type = coerce_type

    def parse(self, value):
        unit_of_measurement = None

        if value and '*' in value:
            value, unit_of_measurement = value.split('*')

        # A value group is not required to have a value, and then coercing does
        # not apply.
        value = self.coerce_type(value) if value is not None else value

        return {
            'value': value,
            'unit': unit_of_measurement
        }
