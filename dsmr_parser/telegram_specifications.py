from decimal import Decimal
from copy import deepcopy

from dsmr_parser import obis_references as obis
from dsmr_parser.parsers import (
    CosemParser,
    ValueParser,
    MBusParser,
    ProfileGenericParser,
    MaxDemandParser,
)
from dsmr_parser.value_types import timestamp
from dsmr_parser.profile_generic_specifications import (
    BUFFER_TYPES,
    PG_HEAD_PARSERS,
    PG_UNIDENTIFIED_BUFFERTYPE_PARSERS,
)

"""
dsmr_parser.telegram_specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains DSMR telegram specifications. Each specifications describes
how the telegram lines are parsed.
"""

V2_2 = {
    "checksum_support": False,
    "objects": {
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
            ValueParser(str),  # changed to str see issue60
            ValueParser(int),
            ValueParser(int),
            ValueParser(str),  # obis ref
            ValueParser(str),  # unit, position 5
            ValueParser(Decimal),  # meter reading, position 6
        ),
    },
}

V3 = V2_2

V4 = {
    "checksum_support": True,
    "objects": {
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
        obis.SHORT_POWER_FAILURE_COUNT: CosemParser(ValueParser(int)),
        obis.LONG_POWER_FAILURE_COUNT: CosemParser(ValueParser(int)),
        obis.POWER_EVENT_FAILURE_LOG: ProfileGenericParser(
            BUFFER_TYPES, PG_HEAD_PARSERS, PG_UNIDENTIFIED_BUFFERTYPE_PARSERS
        ),
        obis.VOLTAGE_SAG_L1_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SAG_L2_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SAG_L3_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SWELL_L1_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SWELL_L2_COUNT: CosemParser(ValueParser(int)),
        obis.VOLTAGE_SWELL_L3_COUNT: CosemParser(ValueParser(int)),
        obis.TEXT_MESSAGE_CODE: CosemParser(ValueParser(int)),
        obis.TEXT_MESSAGE: CosemParser(ValueParser(str)),
        obis.DEVICE_TYPE: CosemParser(ValueParser(int)),
        obis.INSTANTANEOUS_CURRENT_L1: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L2: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L3: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.EQUIPMENT_IDENTIFIER_GAS: CosemParser(ValueParser(str)),
        obis.HOURLY_GAS_METER_READING: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
    },
}

V5 = {
    "checksum_support": True,
    "objects": {
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
        obis.POWER_EVENT_FAILURE_LOG: ProfileGenericParser(
            BUFFER_TYPES, PG_HEAD_PARSERS, PG_UNIDENTIFIED_BUFFERTYPE_PARSERS
        ),
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
            ValueParser(timestamp), ValueParser(Decimal)
        ),
    },
}

ALL = (V2_2, V3, V4, V5)

BELGIUM_FLUVIUS = {
    "checksum_support": True,
    "objects": {
        obis.BELGIUM_VERSION_INFORMATION: CosemParser(ValueParser(str)),
        obis.EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.P1_MESSAGE_TIMESTAMP: CosemParser(ValueParser(timestamp)),
        obis.ELECTRICITY_USED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_USED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_DELIVERED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_DELIVERED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_ACTIVE_TARIFF: CosemParser(ValueParser(str)),
        obis.BELGIUM_CURRENT_AVERAGE_DEMAND: CosemParser(ValueParser(Decimal)),
        obis.BELGIUM_MAXIMUM_DEMAND_MONTH: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
        obis.BELGIUM_MAXIMUM_DEMAND_13_MONTHS: MaxDemandParser(),
        obis.CURRENT_ELECTRICITY_USAGE: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_ELECTRICITY_DELIVERY: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_VOLTAGE_L1: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_VOLTAGE_L2: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_VOLTAGE_L3: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L1: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L2: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L3: CosemParser(ValueParser(Decimal)),
        obis.ACTUAL_SWITCH_POSITION: CosemParser(ValueParser(int)),
        obis.ACTUAL_TRESHOLD_ELECTRICITY: CosemParser(ValueParser(Decimal)),
        obis.BELGIUM_MAX_POWER_PER_PHASE: CosemParser(ValueParser(Decimal)),
        obis.BELGIUM_MAX_CURRENT_PER_PHASE: CosemParser(ValueParser(Decimal)),
        obis.TEXT_MESSAGE: CosemParser(ValueParser(str)),
        obis.BELGIUM_MBUS1_DEVICE_TYPE: CosemParser(ValueParser(int)),
        obis.BELGIUM_MBUS1_EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.BELGIUM_MBUS1_VALVE_POSITION: CosemParser(ValueParser(int)),
        obis.BELGIUM_MBUS1_METER_READING1: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
        obis.BELGIUM_MBUS1_METER_READING2: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
        obis.BELGIUM_MBUS2_DEVICE_TYPE: CosemParser(ValueParser(int)),
        obis.BELGIUM_MBUS2_EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.BELGIUM_MBUS2_VALVE_POSITION: CosemParser(ValueParser(int)),
        obis.BELGIUM_MBUS2_METER_READING1: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
        obis.BELGIUM_MBUS2_METER_READING2: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
        obis.BELGIUM_MBUS3_DEVICE_TYPE: CosemParser(ValueParser(int)),
        obis.BELGIUM_MBUS3_EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.BELGIUM_MBUS3_VALVE_POSITION: CosemParser(ValueParser(int)),
        obis.BELGIUM_MBUS3_METER_READING1: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
        obis.BELGIUM_MBUS3_METER_READING2: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
        obis.BELGIUM_MBUS4_DEVICE_TYPE: CosemParser(ValueParser(int)),
        obis.BELGIUM_MBUS4_EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.BELGIUM_MBUS4_VALVE_POSITION: CosemParser(ValueParser(int)),
        obis.BELGIUM_MBUS4_METER_READING1: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
        obis.BELGIUM_MBUS4_METER_READING2: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
        # DSMR-reader legacy. Should eventually be dropped or selected automatically in a future release.
        obis.BELGIUM_MBUS_WILDCARD_DEVICE_TYPE: CosemParser(ValueParser(int)),
        obis.BELGIUM_MBUS_WILDCARD_EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.BELGIUM_MBUS_WILDCARD_VALVE_POSITION: CosemParser(ValueParser(int)),
        obis.BELGIUM_MBUS_WILDCARD_METER_READING1: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
        obis.BELGIUM_MBUS_WILDCARD_METER_READING2: MBusParser(
            ValueParser(timestamp), ValueParser(Decimal)
        ),
    },
}

LUXEMBOURG_SMARTY = deepcopy(V5)
LUXEMBOURG_SMARTY["objects"].update(
    {
        obis.LUXEMBOURG_EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.ELECTRICITY_IMPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_EXPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
    }
)

# Source: https://www.energiforetagen.se/globalassets/energiforetagen/det-erbjuder-vi/kurser-och-konferenser/elnat/
#         branschrekommendation-lokalt-granssnitt-v2_0-201912.pdf
SWEDEN = {
    "checksum_support": True,
    "objects": {
        obis.P1_MESSAGE_HEADER: CosemParser(ValueParser(str)),
        obis.P1_MESSAGE_TIMESTAMP: CosemParser(ValueParser(timestamp)),
        obis.ELECTRICITY_IMPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_EXPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_ELECTRICITY_USAGE: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_ELECTRICITY_DELIVERY: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_VOLTAGE_L1: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_VOLTAGE_L2: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_VOLTAGE_L3: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L1: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L2: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_CURRENT_L3: CosemParser(ValueParser(Decimal)),
    },
}

Q3D = {
    "checksum_support": False,
    "objects": {
        obis.Q3D_EQUIPMENT_IDENTIFIER: CosemParser(ValueParser(str)),
        obis.ELECTRICITY_IMPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_EXPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_ELECTRICITY_USAGE: CosemParser(ValueParser(Decimal)),
        obis.Q3D_EQUIPMENT_STATE: CosemParser(ValueParser(str)),
        obis.Q3D_EQUIPMENT_SERIALNUMBER: CosemParser(ValueParser(str)),
    },
}


SAGEMCOM_T210_D_R = {
    "general_global_cipher": True,
    "checksum_support": True,
    "objects": {
        obis.P1_MESSAGE_HEADER: CosemParser(ValueParser(str)),
        obis.P1_MESSAGE_TIMESTAMP: CosemParser(ValueParser(timestamp)),
        obis.ELECTRICITY_IMPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_USED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_USED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_ELECTRICITY_USAGE: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_REACTIVE_EXPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_REACTIVE_EXPORTED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_REACTIVE_EXPORTED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_REACTIVE_IMPORTED: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_EXPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_DELIVERED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_DELIVERED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_ELECTRICITY_DELIVERY: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_REACTIVE_IMPORTED_TOTAL: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_REACTIVE_IMPORTED_TARIFF_1: CosemParser(ValueParser(Decimal)),
        obis.ELECTRICITY_REACTIVE_IMPORTED_TARIFF_2: CosemParser(ValueParser(Decimal)),
        obis.CURRENT_REACTIVE_EXPORTED: CosemParser(ValueParser(Decimal)),
    },
}
AUSTRIA_ENERGIENETZE_STEIERMARK = SAGEMCOM_T210_D_R
