from decimal import Decimal
from copy import deepcopy

from dsmr_parser import obis_references as obis
from dsmr_parser.parsers import CosemParser, ValueParser, MBusParser, ProfileGenericParser, MaxDemandParser
from dsmr_parser.value_types import timestamp
from dsmr_parser.profile_generic_specifications import BUFFER_TYPES, PG_HEAD_PARSERS, PG_UNIDENTIFIED_BUFFERTYPE_PARSERS

"""
dsmr_parser.telegram_specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains DSMR telegram specifications. Each specifications describes
how the telegram lines are parsed.
"""

V2_2 = {
    'checksum_support': False,
    'objects': [
        {
            'obis_reference': obis.EQUIPMENT_IDENTIFIER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'EQUIPMENT_IDENTIFIER'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_ACTIVE_TARIFF,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'ELECTRICITY_ACTIVE_TARIFF'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_USAGE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_USAGE'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_DELIVERY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_DELIVERY'
        },
        {
            'obis_reference': obis.ACTUAL_TRESHOLD_ELECTRICITY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ACTUAL_TRESHOLD_ELECTRICITY'
        },
        {
            'obis_reference': obis.ACTUAL_SWITCH_POSITION,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'ACTUAL_SWITCH_POSITION'
        },
        {
            'obis_reference': obis.TEXT_MESSAGE_CODE,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'TEXT_MESSAGE_CODE'
        },
        {
            'obis_reference': obis.TEXT_MESSAGE,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'TEXT_MESSAGE'
        },
        {
            'obis_reference': obis.EQUIPMENT_IDENTIFIER_GAS,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'EQUIPMENT_IDENTIFIER_GAS'
        },
        {
            'obis_reference': obis.DEVICE_TYPE,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'DEVICE_TYPE'
        },
        {
            'obis_reference': obis.VALVE_POSITION_GAS,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'VALVE_POSITION_GAS'
        },
        {
            'obis_reference': obis.GAS_METER_READING,
            'value_parser': MBusParser(
                ValueParser(timestamp),
                ValueParser(str),  # changed to str see issue60
                ValueParser(int),
                ValueParser(int),
                ValueParser(str),  # obis ref
                ValueParser(str),  # unit, position 5
                ValueParser(Decimal),  # meter reading, position 6
            ),
            'value_name': 'GAS_METER_READING'
        },
    ]
}

V3 = V2_2

V4 = {
    'checksum_support': True,
    'objects': [
        {
            'obis_reference': obis.P1_MESSAGE_HEADER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'P1_MESSAGE_HEADER'
        },
        {
            'obis_reference': obis.P1_MESSAGE_TIMESTAMP,
            'value_parser': CosemParser(ValueParser(timestamp)),
            'value_name': 'P1_MESSAGE_TIMESTAMP'
        },
        {
            'obis_reference': obis.EQUIPMENT_IDENTIFIER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'EQUIPMENT_IDENTIFIER'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_ACTIVE_TARIFF,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'ELECTRICITY_ACTIVE_TARIFF'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_USAGE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_USAGE'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_DELIVERY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_DELIVERY'
        },
        {
            'obis_reference': obis.SHORT_POWER_FAILURE_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'SHORT_POWER_FAILURE_COUNT'
        },
        {
            'obis_reference': obis.LONG_POWER_FAILURE_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'LONG_POWER_FAILURE_COUNT'
        },
        {
            'obis_reference': obis.POWER_EVENT_FAILURE_LOG,
            'value_parser': ProfileGenericParser(
                BUFFER_TYPES,
                PG_HEAD_PARSERS,
                PG_UNIDENTIFIED_BUFFERTYPE_PARSERS
            ),
            'value_name': 'POWER_EVENT_FAILURE_LOG'
        },
        {
            'obis_reference': obis.VOLTAGE_SAG_L1_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SAG_L1_COUNT'
        },
        {
            'obis_reference': obis.VOLTAGE_SAG_L2_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SAG_L2_COUNT'
        },
        {
            'obis_reference': obis.VOLTAGE_SAG_L3_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SAG_L3_COUNT'
        },
        {
            'obis_reference': obis.VOLTAGE_SWELL_L1_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SWELL_L1_COUNT'
        },
        {
            'obis_reference': obis.VOLTAGE_SWELL_L2_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SWELL_L2_COUNT'
        },
        {
            'obis_reference': obis.VOLTAGE_SWELL_L3_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SWELL_L3_COUNT'
        },
        {
            'obis_reference': obis.TEXT_MESSAGE_CODE,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'TEXT_MESSAGE_CODE'
        },
        {
            'obis_reference': obis.TEXT_MESSAGE,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'TEXT_MESSAGE'
        },
        {
            'obis_reference': obis.DEVICE_TYPE,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'DEVICE_TYPE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L2'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L3'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE'
        },
        {
            'obis_reference': obis.EQUIPMENT_IDENTIFIER_GAS,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'EQUIPMENT_IDENTIFIER_GAS'
        },
        {
            'obis_reference': obis.HOURLY_GAS_METER_READING,
            'value_parser':  MBusParser(
                ValueParser(timestamp),
                ValueParser(Decimal)
            ),
            'value_name': 'HOURLY_GAS_METER_READING'
        },
    ]
}

V5 = {
    'checksum_support': True,
    'objects': [
        {
            'obis_reference': obis.P1_MESSAGE_HEADER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'P1_MESSAGE_HEADER'
        },
        {
            'obis_reference': obis.P1_MESSAGE_TIMESTAMP,
            'value_parser': CosemParser(ValueParser(timestamp)),
            'value_name': 'P1_MESSAGE_TIMESTAMP'
        },
        {
            'obis_reference': obis.EQUIPMENT_IDENTIFIER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'EQUIPMENT_IDENTIFIER'
        },
        {
            'obis_reference': obis.ELECTRICITY_IMPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_IMPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_ACTIVE_TARIFF,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'ELECTRICITY_ACTIVE_TARIFF'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_USAGE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_USAGE'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_DELIVERY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_DELIVERY'
        },
        {
            'obis_reference': obis.LONG_POWER_FAILURE_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'LONG_POWER_FAILURE_COUNT'
        },
        {
            'obis_reference': obis.SHORT_POWER_FAILURE_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'SHORT_POWER_FAILURE_COUNT'
        },
        {
            'obis_reference': obis.POWER_EVENT_FAILURE_LOG,
            'value_parser': ProfileGenericParser(
                BUFFER_TYPES,
                PG_HEAD_PARSERS,
                PG_UNIDENTIFIED_BUFFERTYPE_PARSERS
            ),
            'value_name': 'POWER_EVENT_FAILURE_LOG'
        },
        {
            'obis_reference': obis.VOLTAGE_SAG_L1_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SAG_L1_COUNT'
        },
        {
            'obis_reference': obis.VOLTAGE_SAG_L2_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SAG_L2_COUNT'
        },
        {
            'obis_reference': obis.VOLTAGE_SAG_L3_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SAG_L3_COUNT'
        },
        {
            'obis_reference': obis.VOLTAGE_SWELL_L1_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SWELL_L1_COUNT'
        },
        {
            'obis_reference': obis.VOLTAGE_SWELL_L2_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SWELL_L2_COUNT'
        },
        {
            'obis_reference': obis.VOLTAGE_SWELL_L3_COUNT,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'VOLTAGE_SWELL_L3_COUNT'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L2'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L3'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L2'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L3'
        },
        {
            'obis_reference': obis.TEXT_MESSAGE,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'TEXT_MESSAGE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE'
        },
        {
            'obis_reference': obis.MBUS_DEVICE_TYPE,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'MBUS_DEVICE_TYPE'
        },
        {
            'obis_reference': obis.MBUS_EQUIPMENT_IDENTIFIER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'MBUS_EQUIPMENT_IDENTIFIER'
        },
        {
            'obis_reference': obis.MBUS_VALVE_POSITION,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'MBUS_VALVE_POSITION'
        },
        {
            'obis_reference': obis.MBUS_METER_READING,
            'value_parser': MBusParser(
                ValueParser(timestamp),
                ValueParser(Decimal)
            ),
            'value_name': 'MBUS_METER_READING'
        },
    ]
}

ALL = (V2_2, V3, V4, V5)

BELGIUM_FLUVIUS = {
    'checksum_support': True,
    'objects': [
        {
            'obis_reference': obis.BELGIUM_VERSION_INFORMATION,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'BELGIUM_VERSION_INFORMATION'
        },
        {
            'obis_reference': obis.BELGIUM_EQUIPMENT_IDENTIFIER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'BELGIUM_EQUIPMENT_IDENTIFIER'
        },
        {
            'obis_reference': obis.P1_MESSAGE_TIMESTAMP,
            'value_parser': CosemParser(ValueParser(timestamp)),
            'value_name': 'P1_MESSAGE_TIMESTAMP'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_ACTIVE_TARIFF,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'ELECTRICITY_ACTIVE_TARIFF'
        },
        {
            'obis_reference': obis.BELGIUM_CURRENT_AVERAGE_DEMAND,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'BELGIUM_CURRENT_AVERAGE_DEMAND'
        },
        {
            'obis_reference': obis.BELGIUM_MAXIMUM_DEMAND_MONTH,
            'value_parser': MBusParser(
                ValueParser(timestamp),
                ValueParser(Decimal)
            ),
            'value_name': 'BELGIUM_MAXIMUM_DEMAND_MONTH'
        },
        {
            'obis_reference': obis.BELGIUM_MAXIMUM_DEMAND_13_MONTHS,
            'value_parser': MaxDemandParser(),
            'value_name': 'BELGIUM_MAXIMUM_DEMAND_13_MONTHS'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_USAGE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_USAGE'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_DELIVERY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_DELIVERY'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L2'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L3'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L2'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L3'
        },
        {
            'obis_reference': obis.ACTUAL_SWITCH_POSITION,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'ACTUAL_SWITCH_POSITION'
        },
        {
            'obis_reference': obis.ACTUAL_TRESHOLD_ELECTRICITY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ACTUAL_TRESHOLD_ELECTRICITY'
        },
        {
            'obis_reference': obis.FUSE_THRESHOLD_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'FUSE_THRESHOLD_L1'
        },
        {
            'obis_reference': obis.TEXT_MESSAGE,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'TEXT_MESSAGE'
        },
        {
            'obis_reference': obis.MBUS_DEVICE_TYPE,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'MBUS_DEVICE_TYPE'
        },
        {
            'obis_reference': obis.MBUS_EQUIPMENT_IDENTIFIER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'MBUS_EQUIPMENT_IDENTIFIER'
        },
        {
            'obis_reference': obis.MBUS_VALVE_POSITION,
            'value_parser': CosemParser(ValueParser(int)),
            'value_name': 'MBUS_VALVE_POSITION'
        },
        {
            'obis_reference': obis.MBUS_METER_READING,
            'value_parser': MBusParser(
                ValueParser(timestamp),
                ValueParser(Decimal)
            ),
            'value_name': 'MBUS_METER_READING'
        },
    ]
}

LUXEMBOURG_SMARTY = deepcopy(V5)
LUXEMBOURG_SMARTY['objects'].extend([  # type: ignore
    {
        'obis_reference': obis.LUXEMBOURG_EQUIPMENT_IDENTIFIER,
        'value_parser': CosemParser(ValueParser(str)),
        'value_name': 'LUXEMBOURG_EQUIPMENT_IDENTIFIER'
    },
    # This is already presented in V5, with the same data
    # {
    #     'obis_reference': obis.ELECTRICITY_IMPORTED_TOTAL,
    #     'value_parser': CosemParser(ValueParser(Decimal)),
    #     'value_name': 'ELECTRICITY_IMPORTED_TOTAL'
    # },
    {
        'obis_reference': obis.ELECTRICITY_EXPORTED_TOTAL,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'ELECTRICITY_EXPORTED_TOTAL'
    }
])

# MSN: Luxembourg Smarty meter (encrypted variant).
#
# Per the official Luxmetering E-Meter P1 Specification v1.1.3 (section 3.2.5):
# - Encryption: AES-128-GCM (DLMS security suite 0)
# - AAD (17 bytes): 0x30 || 00112233445566778899AABBCCDDEEFF
#   The 16-byte authentication key is fixed and identical for all Smarty meters.
#   Users only need to provide the per-meter encryption key (obtained from DSO).
# - IV: system-title (8 bytes) || frame counter (4 bytes)
# - GCM tag length: 12 bytes
#
# The MSN spec extends LUXEMBOURG_SMARTY with the full set of OBIS objects
# defined in Table 3.1 of the official specification.
MSN = deepcopy(LUXEMBOURG_SMARTY)
MSN['general_global_cipher'] = True
# Fixed authentication key for all Luxmetering Smarty meters (public, per spec 3.2.5)
MSN['authentication_key'] = '00112233445566778899AABBCCDDEEFF'
MSN['objects'].extend([  # type: ignore
    {
        'obis_reference': obis.ELECTRICITY_REACTIVE_IMPORTED_TOTAL,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'ELECTRICITY_REACTIVE_IMPORTED_TOTAL'
    },
    {
        'obis_reference': obis.ELECTRICITY_REACTIVE_EXPORTED_TOTAL,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'ELECTRICITY_REACTIVE_EXPORTED_TOTAL'
    },
    {
        'obis_reference': obis.CURRENT_REACTIVE_IMPORTED,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'CURRENT_REACTIVE_IMPORTED'
    },
    {
        'obis_reference': obis.CURRENT_REACTIVE_EXPORTED,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'CURRENT_REACTIVE_EXPORTED'
    },
    {
        'obis_reference': obis.ACTUAL_TRESHOLD_ELECTRICITY,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'ACTUAL_TRESHOLD_ELECTRICITY'
    },
    {
        # Two signed integer values: max imported current, max exported current
        'obis_reference': obis.MSN_CT_RATIO,
        'value_parser': CosemParser(ValueParser(int), ValueParser(int)),
        'value_name': 'MSN_CT_RATIO'
    },
    {
        'obis_reference': obis.MSN_INSTANTANEOUS_APPARENT_POWER_POSITIVE,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'MSN_INSTANTANEOUS_APPARENT_POWER_POSITIVE'
    },
    {
        'obis_reference': obis.MSN_INSTANTANEOUS_APPARENT_POWER_NEGATIVE,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'MSN_INSTANTANEOUS_APPARENT_POWER_NEGATIVE'
    },
    {
        'obis_reference': obis.ACTUAL_SWITCH_POSITION,
        'value_parser': CosemParser(ValueParser(int)),
        'value_name': 'ACTUAL_SWITCH_POSITION'
    },
    {
        'obis_reference': obis.MSN_MBUS_SWITCH_POSITION,
        'value_parser': CosemParser(ValueParser(int)),
        'value_name': 'MSN_MBUS_SWITCH_POSITION'
    },
    {
        'obis_reference': obis.MSN_TEXT_MESSAGE_2,
        'value_parser': CosemParser(ValueParser(str)),
        'value_name': 'MSN_TEXT_MESSAGE_2'
    },
    {
        'obis_reference': obis.MSN_TEXT_MESSAGE_3,
        'value_parser': CosemParser(ValueParser(str)),
        'value_name': 'MSN_TEXT_MESSAGE_3'
    },
    {
        'obis_reference': obis.MSN_TEXT_MESSAGE_4,
        'value_parser': CosemParser(ValueParser(str)),
        'value_name': 'MSN_TEXT_MESSAGE_4'
    },
    {
        'obis_reference': obis.MSN_TEXT_MESSAGE_5,
        'value_parser': CosemParser(ValueParser(str)),
        'value_name': 'MSN_TEXT_MESSAGE_5'
    },
    {
        'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L1_POSITIVE,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L1_POSITIVE'
    },
    {
        'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L2_POSITIVE,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L2_POSITIVE'
    },
    {
        'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L3_POSITIVE,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L3_POSITIVE'
    },
    {
        'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L1_NEGATIVE,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L1_NEGATIVE'
    },
    {
        'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L2_NEGATIVE,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L2_NEGATIVE'
    },
    {
        'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L3_NEGATIVE,
        'value_parser': CosemParser(ValueParser(Decimal)),
        'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L3_NEGATIVE'
    },
])

# Source: https://www.energiforetagen.se/globalassets/energiforetagen/det-erbjuder-vi/kurser-och-konferenser/elnat/
#         branschrekommendation-lokalt-granssnitt-v2_0-201912.pdf
SWEDEN = {
    'checksum_support': True,
    'objects': [
        {
            'obis_reference': obis.P1_MESSAGE_HEADER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'P1_MESSAGE_HEADER'
        },
        {
            'obis_reference': obis.P1_MESSAGE_TIMESTAMP,
            'value_parser': CosemParser(ValueParser(timestamp)),
            'value_name': 'P1_MESSAGE_TIMESTAMP'
        },
        {
            'obis_reference': obis.ELECTRICITY_IMPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_IMPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_EXPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_EXPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_REACTIVE_IMPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_IMPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_REACTIVE_EXPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_EXPORTED_TOTAL'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_USAGE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_USAGE'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_DELIVERY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_DELIVERY'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L1_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L1_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L1_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L1_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L2_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L2_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L2_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L2_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L3_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L3_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_REACTIVE_POWER_L3_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_REACTIVE_POWER_L3_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L2'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L3'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L2'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L3'
        }
    ]
}

Q3D = {
    "checksum_support": False,
    "objects": [
        {
            'obis_reference': obis.Q3D_EQUIPMENT_IDENTIFIER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'Q3D_EQUIPMENT_IDENTIFIER'
        },
        {
            'obis_reference': obis.ELECTRICITY_IMPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_IMPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_EXPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_EXPORTED_TOTAL'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_USAGE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_USAGE'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_DELIVERY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_DELIVERY'
        },
        {
            'obis_reference': obis.Q3D_EQUIPMENT_STATE,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'Q3D_EQUIPMENT_STATE'
        },
        {
            'obis_reference': obis.Q3D_EQUIPMENT_SERIALNUMBER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'Q3D_EQUIPMENT_SERIALNUMBER'
        },
    ]
}


SAGEMCOM_T210_D_R = {
    "general_global_cipher": True,
    "checksum_support": True,
    'objects': [
        {
            'obis_reference': obis.P1_MESSAGE_HEADER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'P1_MESSAGE_HEADER'
        },
        {
            'obis_reference': obis.P1_MESSAGE_TIMESTAMP,
            'value_parser': CosemParser(ValueParser(timestamp)),
            'value_name': 'P1_MESSAGE_TIMESTAMP'
        },
        {
            'obis_reference': obis.ELECTRICITY_IMPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_IMPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_2'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_USAGE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_USAGE'
        },
        {
            'obis_reference': obis.ELECTRICITY_REACTIVE_EXPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_EXPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_REACTIVE_EXPORTED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_EXPORTED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_REACTIVE_EXPORTED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_EXPORTED_TARIFF_2'
        },
        {
            'obis_reference': obis.CURRENT_REACTIVE_IMPORTED,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_REACTIVE_IMPORTED'
        },
        {
            'obis_reference': obis.ELECTRICITY_EXPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_EXPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_2'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_DELIVERY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_DELIVERY'
        },
        {
            'obis_reference': obis.ELECTRICITY_REACTIVE_IMPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_IMPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_REACTIVE_IMPORTED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_IMPORTED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_REACTIVE_IMPORTED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_IMPORTED_TARIFF_2'
        },
        {
            'obis_reference': obis.CURRENT_REACTIVE_EXPORTED,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_REACTIVE_EXPORTED'
        }
    ]
}
AUSTRIA_ENERGIENETZE_STEIERMARK = SAGEMCOM_T210_D_R

ISKRA_IE = {
    "checksum_support": False,
    'objects': [
        {
            'obis_reference': obis.EQUIPMENT_IDENTIFIER_GAS,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'EQUIPMENT_IDENTIFIER_GAS'
        },
        {
            'obis_reference': obis.P1_MESSAGE_TIMESTAMP,
            'value_parser': CosemParser(ValueParser(timestamp)),
            'value_name': 'P1_MESSAGE_TIMESTAMP'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_ACTIVE_TARIFF,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'ELECTRICITY_ACTIVE_TARIFF'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_USAGE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_USAGE'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_DELIVERY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_DELIVERY'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L2'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L3'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L2'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L3'
        },
        {
            'obis_reference': obis.ACTUAL_SWITCH_POSITION,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'ACTUAL_SWITCH_POSITION'
        },
        {
            'obis_reference': obis.TEXT_MESSAGE,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'TEXT_MESSAGE'
        },
        {
            'obis_reference': obis.EQUIPMENT_IDENTIFIER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'EQUIPMENT_IDENTIFIER'
        },
    ]
}

EON_HUNGARY = {
    # Revision: 2023.02.10
    # Based on V5
    # Reference: https://www.eon.hu/content/dam/eon/eon-hungary/documents/Lakossagi/aram/muszaki-ugyek/p1_port%20felhaszn_interfesz_taj_%2020230210.pdf # noqa
    'checksum_support': True,
    'objects': [
        {
            'obis_reference': obis.P1_MESSAGE_TIMESTAMP,
            'value_parser': CosemParser(ValueParser(timestamp)),
            'value_name': 'P1_MESSAGE_TIMESTAMP'
        },
        {
            'obis_reference': obis.LUXEMBOURG_EQUIPMENT_IDENTIFIER,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'COSEM_LOGICAL_DEVICE_NAME'
        },
        {
            'obis_reference': obis.EQUIPMENT_IDENTIFIER_GAS,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'EQUIPMENT_SERIAL_NUMBER'
        },
        {
            'obis_reference': obis.ELECTRICITY_ACTIVE_TARIFF,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'ELECTRICITY_ACTIVE_TARIFF'
        },
        {
            'obis_reference': obis.ACTUAL_SWITCH_POSITION,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'ACTUAL_SWITCH_POSITION'
            # This seems to be wrong in documentation, it's not 0-0:96.50.68, but 0-0:96.3.10
        },
        {
            'obis_reference': obis.ACTUAL_TRESHOLD_ELECTRICITY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ACTUAL_TRESHOLD_ELECTRICITY'
        },
        {
            'obis_reference': obis.ELECTRICITY_IMPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_IMPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_3'
        },
        {
            'obis_reference': obis.ELECTRICITY_USED_TARIFF_4,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_USED_TARIFF_4'
        },
        {
            'obis_reference': obis.ELECTRICITY_EXPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_EXPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_1'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_2'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_3'
        },
        {
            'obis_reference': obis.ELECTRICITY_DELIVERED_TARIFF_4,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_DELIVERED_TARIFF_4'
        },
        {
            'obis_reference': obis.ELECTRICITY_REACTIVE_IMPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_IMPORTED_TOTAL'
        },
        {
            'obis_reference': obis.ELECTRICITY_REACTIVE_EXPORTED_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_EXPORTED_TOTAL'
        },
        {
            'obis_reference': obis.EON_HU_ELECTRICITY_REACTIVE_TOTAL_Q1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_TOTAL_Q1'
        },
        {
            'obis_reference': obis.EON_HU_ELECTRICITY_REACTIVE_TOTAL_Q2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_TOTAL_Q2'
        },
        {
            'obis_reference': obis.EON_HU_ELECTRICITY_REACTIVE_TOTAL_Q3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_TOTAL_Q3'
        },
        {
            'obis_reference': obis.EON_HU_ELECTRICITY_REACTIVE_TOTAL_Q4,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_REACTIVE_TOTAL_Q4'
        },
        {
            'obis_reference': obis.EON_HU_ELECTRICITY_COMBINED,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'ELECTRICITY_COMBINED'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L2'
            # Only with 3 phase meters
        },
        {
            'obis_reference': obis.INSTANTANEOUS_VOLTAGE_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_VOLTAGE_L3'
            # Only with 3 phase meters
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L1'
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L2'
            # Only with 3 phase meters
        },
        {
            'obis_reference': obis.INSTANTANEOUS_CURRENT_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_CURRENT_L3'
            # Only with 3 phase meters
        },
        {
            'obis_reference': obis.EON_HU_INSTANTANEOUS_POWER_FACTOR_TOTAL,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_POWER_FACTOR_TOTAL'
        },
        {
            'obis_reference': obis.EON_HU_INSTANTANEOUS_POWER_FACTOR_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_POWER_FACTOR_L1'
        },
        {
            'obis_reference': obis.EON_HU_INSTANTANEOUS_POWER_FACTOR_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_POWER_FACTOR_L2'
            # Only with 3 phase meters
        },
        {
            'obis_reference': obis.EON_HU_INSTANTANEOUS_POWER_FACTOR_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_POWER_FACTOR_L3'
            # Only with 3 phase meters
        },
        {
            'obis_reference': obis.EON_HU_FREQUENCY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'FREQUENCY'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_USAGE,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_USAGE'
        },
        {
            'obis_reference': obis.CURRENT_ELECTRICITY_DELIVERY,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'CURRENT_ELECTRICITY_DELIVERY'
        },
        {
            'obis_reference': obis.EON_HU_INSTANTANEOUS_REACTIVE_POWER_Q1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_REACTIVE_POWER_Q1'
        },
        {
            'obis_reference': obis.EON_HU_INSTANTANEOUS_REACTIVE_POWER_Q2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_REACTIVE_POWER_Q2'
        },
        {
            'obis_reference': obis.EON_HU_INSTANTANEOUS_REACTIVE_POWER_Q3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_REACTIVE_POWER_Q3'
        },
        {
            'obis_reference': obis.EON_HU_INSTANTANEOUS_REACTIVE_POWER_Q4,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'INSTANTANEOUS_REACTIVE_POWER_Q4'
        },
        {
            'obis_reference': obis.FUSE_THRESHOLD_L1,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'FUSE_THRESHOLD_L1'
        },
        {
            'obis_reference': obis.FUSE_THRESHOLD_L2,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'FUSE_THRESHOLD_L2'
            # Only with 3 phase meters
        },
        {
            'obis_reference': obis.FUSE_THRESHOLD_L3,
            'value_parser': CosemParser(ValueParser(Decimal)),
            'value_name': 'FUSE_THRESHOLD_L3'
            # Only with 3 phase meters
        },
        # I'm not sure which datas does this line containes. It should be the data of last minute of last month.
        # {
        #    'obis_reference': obis.BELGIUM_MAXIMUM_DEMAND_13_MONTHS,
        #    'value_parser': NonExistingParser(
        #        ValueParser(timestamp),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal),
        #        ValueParser(Decimal)
        #    ),
        #    'value_name': 'LAST_MONTH_DATA'
        # },
        {
            'obis_reference': obis.TEXT_MESSAGE,
            'value_parser': CosemParser(ValueParser(str)),
            'value_name': 'TEXT_MESSAGE'
        }
    ]
}
