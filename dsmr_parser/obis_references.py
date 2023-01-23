"""
Contains the signatures of each telegram line.

Previously contained the channel + obis reference signatures, but has been
refactored to full line signatures to maintain backwards compatibility.
Might be refactored in a backwards incompatible way as soon as proper telegram
objects are introduced.
"""
P1_MESSAGE_HEADER = r"\d-\d:0\.2\.8.+?\r\n"
P1_MESSAGE_TIMESTAMP = r"\d-\d:1\.0\.0.+?\r\n"
ELECTRICITY_USED_TARIFF_1 = r"\d-\d:1\.8\.1.+?\r\n"
ELECTRICITY_USED_TARIFF_2 = r"\d-\d:1\.8\.2.+?\r\n"
ELECTRICITY_DELIVERED_TARIFF_1 = r"\d-\d:2\.8\.1.+?\r\n"
ELECTRICITY_DELIVERED_TARIFF_2 = r"\d-\d:2\.8\.2.+?\r\n"
CURRENT_REACTIVE_EXPORTED = r"\d-\d:3\.7\.0.+?\r\n"
ELECTRICITY_REACTIVE_IMPORTED_TOTAL = r"\d-\d:3\.8\.0.+?\r\n"
ELECTRICITY_REACTIVE_IMPORTED_TARIFF_1 = r"\d-\d:3\.8\.1.+?\r\n"
ELECTRICITY_REACTIVE_IMPORTED_TARIFF_2 = r"\d-\d:3\.8\.2.+?\r\n"
CURRENT_REACTIVE_IMPORTED = r"\d-\d:4\.7\.0.+?\r\n"
ELECTRICITY_REACTIVE_EXPORTED_TOTAL = r"\d-\d:4\.8\.0.+?\r\n"
ELECTRICITY_REACTIVE_EXPORTED_TARIFF_1 = r"\d-\d:4\.8\.1.+?\r\n"
ELECTRICITY_REACTIVE_EXPORTED_TARIFF_2 = r"\d-\d:4\.8\.2.+?\r\n"
ELECTRICITY_ACTIVE_TARIFF = r"\d-\d:96\.14\.0.+?\r\n"
EQUIPMENT_IDENTIFIER = r"\d-\d:96\.1\.1.+?\r\n"
CURRENT_ELECTRICITY_USAGE = r"\d-\d:1\.7\.0.+?\r\n"
CURRENT_ELECTRICITY_DELIVERY = r"\d-\d:2\.7\.0.+?\r\n"
LONG_POWER_FAILURE_COUNT = r"96\.7\.9.+?\r\n"
SHORT_POWER_FAILURE_COUNT = r"96\.7\.21.+?\r\n"
POWER_EVENT_FAILURE_LOG = r"99\.97\.0.+?\r\n"
VOLTAGE_SAG_L1_COUNT = r"\d-\d:32\.32\.0.+?\r\n"
VOLTAGE_SAG_L2_COUNT = r"\d-\d:52\.32\.0.+?\r\n"
VOLTAGE_SAG_L3_COUNT = r"\d-\d:72\.32\.0.+?\r\n"
VOLTAGE_SWELL_L1_COUNT = r"\d-\d:32\.36\.0.+?\r\n"
VOLTAGE_SWELL_L2_COUNT = r"\d-\d:52\.36\.0.+?\r\n"
VOLTAGE_SWELL_L3_COUNT = r"\d-\d:72\.36\.0.+?\r\n"
INSTANTANEOUS_VOLTAGE_L1 = r"\d-\d:32\.7\.0.+?\r\n"
INSTANTANEOUS_VOLTAGE_L2 = r"\d-\d:52\.7\.0.+?\r\n"
INSTANTANEOUS_VOLTAGE_L3 = r"\d-\d:72\.7\.0.+?\r\n"
INSTANTANEOUS_CURRENT_L1 = r"\d-\d:31\.7\.0.+?\r\n"
INSTANTANEOUS_CURRENT_L2 = r"\d-\d:51\.7\.0.+?\r\n"
INSTANTANEOUS_CURRENT_L3 = r"\d-\d:71\.7\.0.+?\r\n"
TEXT_MESSAGE_CODE = r"\d-\d:96\.13\.1.+?\r\n"
TEXT_MESSAGE = r"\d-\d:96\.13\.0.+?\r\n"
DEVICE_TYPE = r"\d-\d:24\.1\.0.+?\r\n"
INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE = r"\d-\d:21\.7\.0.+?\r\n"
INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE = r"\d-\d:41\.7\.0.+?\r\n"
INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE = r"\d-\d:61\.7\.0.+?\r\n"
INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE = r"\d-\d:22\.7\.0.+?\r\n"
INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE = r"\d-\d:42\.7\.0.+?\r\n"
INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE = r"\d-\d:62\.7\.0.+?\r\n"
EQUIPMENT_IDENTIFIER_GAS = r"\d-\d:96\.1\.0.+?\r\n"
# TODO differences between gas meter readings in v3 and lower and v4 and up
HOURLY_GAS_METER_READING = r"\d-\d:24\.2\.1.+?\r\n"
GAS_METER_READING = r"\d-\d:24\.3\.0.+?\r\n.+?\r\n"
ACTUAL_TRESHOLD_ELECTRICITY = r"\d-\d:17\.0\.0.+?\r\n"
ACTUAL_SWITCH_POSITION = r"\d-\d:96\.3\.10.+?\r\n"
VALVE_POSITION_GAS = r"\d-\d:24\.4\.0.+?\r\n"

# TODO 17.0.0
# TODO 96.3.10

ELECTRICITY_USED_TARIFF_ALL = (ELECTRICITY_USED_TARIFF_1, ELECTRICITY_USED_TARIFF_2)
ELECTRICITY_DELIVERED_TARIFF_ALL = (
    ELECTRICITY_DELIVERED_TARIFF_1,
    ELECTRICITY_DELIVERED_TARIFF_2,
)

# International generalized additions
ELECTRICITY_IMPORTED_TOTAL = (
    r"\d-\d:1\.8\.0.+?\r\n"  # Total imported energy register (P+)
)
ELECTRICITY_EXPORTED_TOTAL = (
    r"\d-\d:2\.8\.0.+?\r\n"  # Total exported energy register (P-)
)

# International non generalized additions (country specific) / risk for necessary refactoring
BELGIUM_VERSION_INFORMATION = r"\d-\d:96\.1\.4.+?\r\n"
BELGIUM_EQUIPMENT_IDENTIFIER = r"\d-0:96\.1\.1.+?\r\n"
BELGIUM_CURRENT_AVERAGE_DEMAND = r"\d-\d:1\.4\.0.+?\r\n"
BELGIUM_MAXIMUM_DEMAND_MONTH = r"\d-\d:1\.6\.0.+?\r\n"
BELGIUM_MAXIMUM_DEMAND_13_MONTHS = r"\d-\d:98\.1\.0.+?\r\n"
BELGIUM_MAX_POWER_PER_PHASE = (
    r"\d-\d:17\.0\.0.+?\r\n"  # Applicable when power limitation is active
)
BELGIUM_MAX_CURRENT_PER_PHASE = (
    r"\d-\d:31\.4\.0.+?\r\n"  # Applicable when current limitation is active
)

# Multiple 'slaves' can be linked to the main device.
# Mostly MBUS1 = GAS METER with values on 24.2.3
# While WATER METER reports it's values on 24.2.1
# The GAS METER also reports its valve state on 24.4.0
# Dev type for gas = 7 and water = 8
BELGIUM_MBUS1_DEVICE_TYPE = r"\d-1:24\.1\.0.+?\r\n"
BELGIUM_MBUS1_EQUIPMENT_IDENTIFIER = r"\d-1:96\.1\.1.+?\r\n"
BELGIUM_MBUS1_VALVE_POSITION = r"\d-1:24\.4\.0.+?\r\n"
BELGIUM_MBUS1_METER_READING1 = r"\d-1:24\.2\.1.+?\r\n"
BELGIUM_MBUS1_METER_READING2 = r"\d-1:24\.2\.3.+?\r\n"

BELGIUM_MBUS2_DEVICE_TYPE = r"\d-2:24\.1\.0.+?\r\n"
BELGIUM_MBUS2_EQUIPMENT_IDENTIFIER = r"\d-2:96\.1\.1.+?\r\n"
BELGIUM_MBUS2_VALVE_POSITION = r"\d-2:24\.4\.0.+?\r\n"
BELGIUM_MBUS2_METER_READING1 = r"\d-2:24\.2\.1.+?\r\n"
BELGIUM_MBUS2_METER_READING2 = r"\d-2:24\.2\.3.+?\r\n"

BELGIUM_MBUS3_DEVICE_TYPE = r"\d-3:24\.1\.0.+?\r\n"
BELGIUM_MBUS3_EQUIPMENT_IDENTIFIER = r"\d-3:96\.1\.1.+?\r\n"
BELGIUM_MBUS3_VALVE_POSITION = r"\d-3:24\.4\.0.+?\r\n"
BELGIUM_MBUS3_METER_READING1 = r"\d-3:24\.2\.1.+?\r\n"
BELGIUM_MBUS3_METER_READING2 = r"\d-3:24\.2\.3.+?\r\n"

BELGIUM_MBUS4_DEVICE_TYPE = r"\d-4:24\.1\.0.+?\r\n"
BELGIUM_MBUS4_EQUIPMENT_IDENTIFIER = r"\d-4:96\.1\.1.+?\r\n"
BELGIUM_MBUS4_VALVE_POSITION = r"\d-4:24\.4\.0.+?\r\n"
BELGIUM_MBUS4_METER_READING1 = r"\d-4:24\.2\.1.+?\r\n"
BELGIUM_MBUS4_METER_READING2 = r"\d-4:24\.2\.3.+?\r\n"

# DSMR-reader legacy. Should eventually be dropped or selected automatically in a future release.
BELGIUM_MBUS_WILDCARD_DEVICE_TYPE = r"\d-\d:24\.1\.0.+?\r\n"
BELGIUM_MBUS_WILDCARD_EQUIPMENT_IDENTIFIER = r"\d-\d:96\.1\.1.+?\r\n"
BELGIUM_MBUS_WILDCARD_VALVE_POSITION = r"\d-\d:24\.4\.0.+?\r\n"
BELGIUM_MBUS_WILDCARD_METER_READING1 = r"\d-\d:24\.2\.1.+?\r\n"
BELGIUM_MBUS_WILDCARD_METER_READING2 = r"\d-\d:24\.2\.3.+?\r\n"


LUXEMBOURG_EQUIPMENT_IDENTIFIER = r"\d-\d:42\.0\.0.+?\r\n"  # Logical device name

Q3D_EQUIPMENT_IDENTIFIER = r"\d-\d:0\.0\.0.+?\r\n"  # Logical device name
Q3D_EQUIPMENT_STATE = r"\d-\d:96\.5\.5.+?\r\n"  # Device state (hexadecimal)
Q3D_EQUIPMENT_SERIALNUMBER = r"\d-\d:96\.1\.255.+?\r\n"  # Device Serialnumber
