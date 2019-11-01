from decimal import Decimal

from dsmr_parser import obis_references as obis
from dsmr_parser.parsers import CosemParser, ValueParser, MBusParser
from dsmr_parser.value_types import timestamp


"""
dsmr_parser.telegram_specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains DSMR telegram specifications. Each specifications describes
how the telegram lines are parsed.
"""

V2_2 = {
    'checksum_support': False,
    'objects': {
        obis.EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.ELECTRICITY_USED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_USED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_DELIVERED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_DELIVERED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_ACTIVE_TARIFF: CosemParser(ValueParser(str)),
        obis.CURRENT_ELECTRICITY_USAGE: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_ELECTRICITY_DELIVERY: CosemParser(ValueParser(Decimal)),
        obis.ACTUAL_TRESHOLD_ELECTRICITY: CosemParser(ValueParser(Decimal)),
        obis.ACTUAL_SWITCH_POSITION: CosemParser(ValueParser(str)),
        obis.TEXT_MESSAGE_CODE: CosemParser(ValueParser(int)),
        obis.TEXT_MESSAGE: CosemParser(ValueParser(str)),
        obis.EQUIPMENT_IDENTIFIER_GAS: CosemParser(ValueParser(str)),
        obis.DEVICE_TYPE: CosemParser(ValueParser(str)),
        obis.VALVE_POSITION_GAS: CosemParser(ValueParser(str)),
        obis.GAS_METER_READING: MBusParser(
            ValueParser(timestamp),
            ValueParser(str),  # DS: Changed from int
            ValueParser(int),
            ValueParser(int),
            ValueParser(str),
            ValueParser(Decimal),
        ),
    }
}

V3 = V2_2

V4 = {
    'checksum_support': True,
    'objects': {
        obis.P1_MESSAGE_HEADER: CosemParser(ValueParser(str)),
        obis.P1_MESSAGE_TIMESTAMP: CosemParser(ValueParser(timestamp)),
        obis.EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.ELECTRICITY_USED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_USED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_DELIVERED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_DELIVERED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_ACTIVE_TARIFF: CosemParser(ValueParser(str)),
        obis.CURRENT_ELECTRICITY_USAGE: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_ELECTRICITY_DELIVERY: CosemParser(ValueParser(Decimal)),
        obis.LONG_POWER_FAILURE_COUNT: CosemParser(ValueParser(int)),
        # POWER_EVENT_FAILURE_LOG: ProfileGenericParser(), TODO
        obis.VOLTAGE_SAG_L1_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SAG_L2_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SAG_L3_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SWELL_L1_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SWELL_L2_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SWELL_L3_COUNT: CosemParser(ValueParser(int)),
        obis.TEXT_MESSAGE_CODE: CosemParser(ValueParser(int)),
        obis.TEXT_MESSAGE: CosemParser(ValueParser(str)),
        obis.DEVICE_TYPE: CosemParser(ValueParser(int)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.EQUIPMENT_IDENTIFIER_GAS: CosemParser(ValueParser(str)),
        obis.HOURLY_GAS_METER_READING: MBusParser(
            ValueParser(timestamp),
            ValueParser(Decimal)
        )
    }
}

V5 = {
    'checksum_support': True,
    'objects': {
        obis.P1_MESSAGE_HEADER: CosemParser(ValueParser(str)),
        obis.P1_MESSAGE_TIMESTAMP: CosemParser(ValueParser(timestamp)),
        obis.EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.ELECTRICITY_IMPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_USED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_USED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_DELIVERED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_DELIVERED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_ACTIVE_TARIFF: CosemParser(ValueParser(str)),
        obis.CURRENT_ELECTRICITY_USAGE: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_ELECTRICITY_DELIVERY: CosemParser(ValueParser(Decimal)),
        obis.LONG_POWER_FAILURE_COUNT: CosemParser(ValueParser(int)),
        obis.SHORT_POWER_FAILURE_COUNT: CosemParser(ValueParser(int)),
        # POWER_EVENT_FAILURE_LOG: ProfileGenericParser(), TODO
        obis.VOLTAGE_SAG_L1_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SAG_L2_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SAG_L3_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SWELL_L1_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SWELL_L2_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SWELL_L3_COUNT: CosemParser(ValueParser(int)),
        obis.INSTANTANEOUS_VOLTAGE_L1: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_VOLTAGE_L2: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_VOLTAGE_L3: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L1: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L2: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L3: CosemParser(ValueParser(Decimal)),
        obis.TEXT_MESSAGE: CosemParser(ValueParser(str)),
        obis.DEVICE_TYPE: CosemParser(ValueParser(int)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.EQUIPMENT_IDENTIFIER_GAS: CosemParser(ValueParser(str)),
        obis.HOURLY_GAS_METER_READING: MBusParser(
            ValueParser(timestamp),
            ValueParser(Decimal)
        )
    }
}

ALL = (V2_2, V3, V4, V5)
