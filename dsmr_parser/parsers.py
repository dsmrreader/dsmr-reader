import logging
import re

from ctypes import c_ushort

from dsmr_parser.objects import MBusObject, CosemObject, ProfileGenericObject
from dsmr_parser.exceptions import ParseError, InvalidChecksumError

logger = logging.getLogger(__name__)


class TelegramParser(object):
    crc16_tab = []

    def __init__(self, telegram_specification, apply_checksum_validation=True):
        """
        :param telegram_specification: determines how the telegram is parsed
        :param apply_checksum_validation: validate checksum if applicable for
            telegram DSMR version (v4 and up).
        :type telegram_specification: dict
        """
        self.telegram_specification = telegram_specification
        self.apply_checksum_validation = apply_checksum_validation

    def parse(self, telegram_data):
        """
        Parse telegram from string to dict.

        The telegram str type makes python 2.x integration easier.

        :param str telegram_data: full telegram from start ('/') to checksum
            ('!ABCD') including line endings in between the telegram's lines
        :rtype: dict
        :returns: Shortened example:
            {
                ..
                ..
            }
        :raises ParseError:
        :raises InvalidChecksumError:
        """

        if (
            self.apply_checksum_validation
            and self.telegram_specification["checksum_support"]
        ):
            self.validate_checksum(telegram_data)

        telegram = {}

        for signature, parser in self.telegram_specification["objects"].items():
            # DSMR-reader #778: We might hit the same pattern multiple times. The last one matched will be leading.
            matches = re.findall(signature, telegram_data, re.DOTALL)

            for current_match in matches:
                # Some signatures are optional and may not be present,
                # so only parse lines that match
                try:
                    telegram[signature] = parser.parse(current_match)
                except Exception:
                    logger.error(
                        "ignore line with signature {}, because parsing failed.".format(
                            signature
                        ),
                        exc_info=True,
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
        checksum_contents = re.search(r"\/.+\!", telegram, re.DOTALL)

        # Extract the hexadecimal checksum value itself.
        # The line ending '\r\n' for the checksum line can be ignored.
        checksum_hex = re.search(r"((?<=\!)[0-9A-Z]{4})+", telegram)

        if not checksum_contents or not checksum_hex:
            raise ParseError(
                "Failed to perform CRC validation because the telegram is "
                "incomplete. The checksum and/or content values are missing."
            )

        calculated_crc = TelegramParser.crc16(checksum_contents.group(0))
        expected_crc = int(checksum_hex.group(0), base=16)
        calculated_crc_hex = "{:0>4}".format(hex(calculated_crc)[2:].upper())
        expected_crc_hex = "{:0>4}".format(hex(expected_crc)[2:].upper())

        if calculated_crc != expected_crc:
            raise InvalidChecksumError(
                "Invalid telegram CRC. The calculated checksum '{}' ({}) does not match the "
                "telegram checksum '{}' ({})".format(
                    calculated_crc, calculated_crc_hex, expected_crc, expected_crc_hex
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
                for _j in range(0, 8):
                    if crc & 0x0001:
                        crc = c_ushort(crc >> 1).value ^ 0xA001
                    else:
                        crc = c_ushort(crc >> 1).value
                TelegramParser.crc16_tab.append(hex(crc))

        for c in telegram:
            d = ord(c)
            tmp = crcValue ^ d
            rotated = c_ushort(crcValue >> 8).value
            crcValue = rotated ^ int(TelegramParser.crc16_tab[(tmp & 0x00FF)], 0)

        return crcValue


class DSMRObjectParser(object):
    """
    Parses an object (can also be see as a 'line') from a telegram.
    """

    def __init__(self, *value_formats):
        self.value_formats = value_formats

    def _is_line_wellformed(self, line, values):
        # allows overriding by child class
        return values and (len(values) == len(self.value_formats))

    def _parse_values(self, values):
        # allows overriding by child class
        return [self.value_formats[i].parse(value) for i, value in enumerate(values)]

    def _parse(self, line):
        # Match value groups, but exclude the parentheses
        pattern = re.compile(r"((?<=\()[0-9a-zA-Z\.\*\-\:]{0,}(?=\)))")

        values = re.findall(pattern, line)

        if not self._is_line_wellformed(line, values):
            raise ParseError("Invalid '%s' line for '%s'", line, self)

        # Convert empty value groups to None for clarity.
        values = [None if value == "" else value for value in values]

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
        return MBusObject(self._parse(line))


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
        return CosemObject(self._parse(line))


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
        self.value_formats = head_parsers
        self.buffer_types = buffer_types
        self.parsers_for_unidentified = parsers_for_unidentified

    def _is_line_wellformed(self, line, values):
        if values and (len(values) == 1) and (values[0] == ""):
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
        if buffer_length > 0:
            if buffer_value_obis_ID in self.buffer_types:
                bufferValueParsers = self.buffer_types[buffer_value_obis_ID]
            else:
                bufferValueParsers = self.parsers_for_unidentified
        # add the parsers for the encountered value type z times
        for _ in range(buffer_length):
            self.value_formats.extend(bufferValueParsers)

        return [self.value_formats[i].parse(value) for i, value in enumerate(values)]

    def parse(self, line):
        return ProfileGenericObject(self._parse(line))


class ValueParser(object):
    """
    Parses a single value from DSMRObject's.

    Example with coerce_type being int:
        (002*A) becomes {'value': 1, 'unit': 'A'}

    Example with coerce_type being str:
        (42) becomes {'value': '42', 'unit': None}
    """

    def __init__(self, coerce_type):
        self.coerce_type = coerce_type

    def parse(self, value):
        unit_of_measurement = None

        if value and "*" in value:
            value, unit_of_measurement = value.split("*")

        # A value group is not required to have a value, and then coercing does
        # not apply.
        value = self.coerce_type(value) if value is not None else value

        return {"value": value, "unit": unit_of_measurement}
