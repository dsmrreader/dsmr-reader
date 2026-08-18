"""
Contains the signatures of each telegram line.

Previously contained the channel + obis reference signatures, but has been
refactored to full line signatures to maintain backwards compatibility.
Might be refactored in a backwards incompatible way as soon as proper telegram
objects are introduced.
"""
P1_MESSAGE_HEADER = r'^\d-\d:0\.2\.8.+?\r\n'
P1_MESSAGE_TIMESTAMP = r'^\d-\d:1\.0\.0.+?\r\n'
ELECTRICITY_USED_TARIFF_1 = r'^\d-\d:1\.8\.1.+?\r\n'
ELECTRICITY_USED_TARIFF_2 = r'^\d-\d:1\.8\.2.+?\r\n'
ELECTRICITY_USED_TARIFF_3 = r'^\d-\d:1\.8\.3.+?\r\n'
ELECTRICITY_USED_TARIFF_4 = r'^\d-\d:1\.8\.4.+?\r\n'
ELECTRICITY_DELIVERED_TARIFF_1 = r'^\d-\d:2\.8\.1.+?\r\n'
ELECTRICITY_DELIVERED_TARIFF_2 = r'^\d-\d:2\.8\.2.+?\r\n'
ELECTRICITY_DELIVERED_TARIFF_3 = r'^\d-\d:2\.8\.3.+?\r\n'
ELECTRICITY_DELIVERED_TARIFF_4 = r'^\d-\d:2\.8\.4.+?\r\n'
CURRENT_REACTIVE_IMPORTED = r'^\d-\d:3\.7\.0.+?\r\n'
ELECTRICITY_REACTIVE_IMPORTED_TOTAL = r'^\d-\d:3\.8\.0.+?\r\n'
ELECTRICITY_REACTIVE_IMPORTED_TARIFF_1 = r'^\d-\d:3\.8\.1.+?\r\n'
ELECTRICITY_REACTIVE_IMPORTED_TARIFF_2 = r'^\d-\d:3\.8\.2.+?\r\n'
CURRENT_REACTIVE_EXPORTED = r'^\d-\d:4\.7\.0.+?\r\n'
ELECTRICITY_REACTIVE_EXPORTED_TOTAL = r'^\d-\d:4\.8\.0.+?\r\n'
ELECTRICITY_REACTIVE_EXPORTED_TARIFF_1 = r'^\d-\d:4\.8\.1.+?\r\n'
ELECTRICITY_REACTIVE_EXPORTED_TARIFF_2 = r'^\d-\d:4\.8\.2.+?\r\n'
ELECTRICITY_ACTIVE_TARIFF = r'^\d-\d:96\.14\.0.+?\r\n'
EQUIPMENT_IDENTIFIER = r'^\d-\d:96\.1\.1.+?\r\n'
CURRENT_ELECTRICITY_USAGE = r'^\d-\d:1\.7\.0.+?\r\n'
CURRENT_ELECTRICITY_DELIVERY = r'^\d-\d:2\.7\.0.+?\r\n'
LONG_POWER_FAILURE_COUNT = r'^\d-\d:96\.7\.9.+?\r\n'
SHORT_POWER_FAILURE_COUNT = r'^\d-\d:96\.7\.21.+?\r\n'
POWER_EVENT_FAILURE_LOG = r'^\d-\d:99\.97\.0.+?\r\n'
VOLTAGE_SAG_L1_COUNT = r'^\d-\d:32\.32\.0.+?\r\n'
VOLTAGE_SAG_L2_COUNT = r'^\d-\d:52\.32\.0.+?\r\n'
VOLTAGE_SAG_L3_COUNT = r'^\d-\d:72\.32\.0.+?\r\n'
VOLTAGE_SWELL_L1_COUNT = r'^\d-\d:32\.36\.0.+?\r\n'
VOLTAGE_SWELL_L2_COUNT = r'^\d-\d:52\.36\.0.+?\r\n'
VOLTAGE_SWELL_L3_COUNT = r'^\d-\d:72\.36\.0.+?\r\n'
INSTANTANEOUS_VOLTAGE_L1 = r'^\d-\d:32\.7\.0.+?\r\n'
INSTANTANEOUS_VOLTAGE_L2 = r'^\d-\d:52\.7\.0.+?\r\n'
INSTANTANEOUS_VOLTAGE_L3 = r'^\d-\d:72\.7\.0.+?\r\n'
INSTANTANEOUS_CURRENT_L1 = r'^\d-\d:31\.7\.0.+?\r\n'
INSTANTANEOUS_CURRENT_L2 = r'^\d-\d:51\.7\.0.+?\r\n'
INSTANTANEOUS_CURRENT_L3 = r'^\d-\d:71\.7\.0.+?\r\n'
FUSE_THRESHOLD_L1 = r'^\d-\d:31\.4\.0.+?\r\n'  # Applicable when current limitation is active
FUSE_THRESHOLD_L2 = r'^\d-\d:51\.4\.0.+?\r\n'  # Applicable when current limitation is active
FUSE_THRESHOLD_L3 = r'^\d-\d:71\.4\.0.+?\r\n'  # Applicable when current limitation is active
TEXT_MESSAGE_CODE = r'^\d-\d:96\.13\.1.+?\r\n'
TEXT_MESSAGE = r'^\d-\d:96\.13\.0.+?\r\n'
DEVICE_TYPE = r'^\d-\d:24\.1\.0.+?\r\n'
INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE = r'^\d-\d:21\.7\.0.+?\r\n'
INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE = r'^\d-\d:41\.7\.0.+?\r\n'
INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE = r'^\d-\d:61\.7\.0.+?\r\n'
INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE = r'^\d-\d:22\.7\.0.+?\r\n'
INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE = r'^\d-\d:42\.7\.0.+?\r\n'
INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE = r'^\d-\d:62\.7\.0.+?\r\n'
INSTANTANEOUS_REACTIVE_POWER_L1_POSITIVE = r'^\d-\d:23\.7\.0.+?\r\n'
INSTANTANEOUS_REACTIVE_POWER_L1_NEGATIVE = r'^\d-\d:24\.7\.0.+?\r\n'
INSTANTANEOUS_REACTIVE_POWER_L2_POSITIVE = r'^\d-\d:43\.7\.0.+?\r\n'
INSTANTANEOUS_REACTIVE_POWER_L2_NEGATIVE = r'^\d-\d:44\.7\.0.+?\r\n'
INSTANTANEOUS_REACTIVE_POWER_L3_POSITIVE = r'^\d-\d:63\.7\.0.+?\r\n'
INSTANTANEOUS_REACTIVE_POWER_L3_NEGATIVE = r'^\d-\d:64\.7\.0.+?\r\n'
EQUIPMENT_IDENTIFIER_GAS = r'^\d-\d:96\.1\.0.+?\r\n'
# TODO differences between gas meter readings in v3 and lower and v4 and up
HOURLY_GAS_METER_READING = r'^\d-\d:24\.2\.1.+?\r\n'
GAS_METER_READING = r'^\d-\d:24\.3\.0.+?\r\n.+?\r\n'
ACTUAL_TRESHOLD_ELECTRICITY = r'^\d-\d:17\.0\.0.+?\r\n'
ACTUAL_SWITCH_POSITION = r'^\d-\d:96\.3\.10.+?\r\n'
VALVE_POSITION_GAS = r'^\d-\d:24\.4\.0.+?\r\n'

# Multiple 'slaves' can be linked to the main device.
# The type is reported on 24.1.0
# Specifications are in EN 13757-3
# For example: Water mater = 7, Gas meter = 3
# Identifier is on 96.1.0 (in NL for ex) or
# on 96.1.1 (in BE for ex)
# The values are reported on 24.2.1
# With an exception in Belgium for the GAS meter
# Be aware that for the gas volume, another OBIS-code is published
# than the one listed in section 7 of DSMR P1.
# This is due to the fact that in Belgium the not-temperature
# corrected gas volume is used while in the Netherlands,
# the temperature corrected gas volume is used.
MBUS_DEVICE_TYPE = r'^\d-[1-9]:24\.1\.0.+?\r\n'
MBUS_EQUIPMENT_IDENTIFIER = r'^\d-[1-9]:96\.1\.[01].+?\r\n'
MBUS_VALVE_POSITION = r'^\d-[1-9]:24\.4\.0.+?\r\n'
MBUS_METER_READING = r'^\d-[1-9]:24\.2\.[13].+?\r\n'

# TODO 17.0.0

ELECTRICITY_USED_TARIFF_ALL = (
    ELECTRICITY_USED_TARIFF_1,
    ELECTRICITY_USED_TARIFF_2
)
ELECTRICITY_DELIVERED_TARIFF_ALL = (
    ELECTRICITY_DELIVERED_TARIFF_1,
    ELECTRICITY_DELIVERED_TARIFF_2
)

# International generalized additions
ELECTRICITY_IMPORTED_TOTAL = r'^\d-\d:1\.8\.0.+?\r\n'  # Total imported energy register (P+)
ELECTRICITY_EXPORTED_TOTAL = r'^\d-\d:2\.8\.0.+?\r\n'  # Total exported energy register (P-)

# International non generalized additions (country specific) / risk for necessary refactoring
BELGIUM_VERSION_INFORMATION = r'^\d-\d:96\.1\.4.+?\r\n'
BELGIUM_EQUIPMENT_IDENTIFIER = r'^\d-0:96\.1\.1.+?\r\n'
BELGIUM_CURRENT_AVERAGE_DEMAND = r'^\d-\d:1\.4\.0.+?\r\n'
BELGIUM_MAXIMUM_DEMAND_MONTH = r'^\d-\d:1\.6\.0.+?\r\n'
BELGIUM_MAXIMUM_DEMAND_13_MONTHS = r'^\d-\d:98\.1\.0.+?\r\n'

LUXEMBOURG_EQUIPMENT_IDENTIFIER = r'^\d-\d:42\.0\.0.+?\r\n'  # Logical device name

# MSN (Luxembourg Smarty encrypted meter) specific references
MSN_INSTANTANEOUS_APPARENT_POWER_POSITIVE = r'^\d-\d:9\.7\.0.+?\r\n'   # S+ (kVA)
MSN_INSTANTANEOUS_APPARENT_POWER_NEGATIVE = r'^\d-\d:10\.7\.0.+?\r\n'  # S- (kVA)
MSN_CT_RATIO = r'^1-1:31\.4\.0.+?\r\n'          # Current transformer ratio (import/export threshold)
MSN_MBUS_SWITCH_POSITION = r'^\d-[1-9]:96\.3\.10.+?\r\n'  # MBus device breaker state
MSN_TEXT_MESSAGE_2 = r'^\d-\d:96\.13\.2.+?\r\n'
MSN_TEXT_MESSAGE_3 = r'^\d-\d:96\.13\.3.+?\r\n'
MSN_TEXT_MESSAGE_4 = r'^\d-\d:96\.13\.4.+?\r\n'
MSN_TEXT_MESSAGE_5 = r'^\d-\d:96\.13\.5.+?\r\n'

Q3D_EQUIPMENT_IDENTIFIER = r'^\d-\d:0\.0\.0.+?\r\n'  # Logical device name
Q3D_EQUIPMENT_STATE = r'^\d-\d:96\.5\.5.+?\r\n'  # Device state (hexadecimal)
Q3D_EQUIPMENT_SERIALNUMBER = r'^\d-\d:96\.1\.255.+?\r\n'  # Device Serialnumber

# EON Hungary
EON_HU_ELECTRICITY_REACTIVE_TOTAL_Q1 = r'^\d-\d:5\.8\.0.+?\r\n'
EON_HU_ELECTRICITY_REACTIVE_TOTAL_Q2 = r'^\d-\d:6\.8\.0.+?\r\n'
EON_HU_ELECTRICITY_REACTIVE_TOTAL_Q3 = r'^\d-\d:7\.8\.0.+?\r\n'
EON_HU_ELECTRICITY_REACTIVE_TOTAL_Q4 = r'^\d-\d:8\.8\.0.+?\r\n'
EON_HU_ELECTRICITY_COMBINED = r'^\d-\d:15\.8\.0.+?\r\n'
EON_HU_INSTANTANEOUS_POWER_FACTOR_TOTAL = r'^\d-\d:13\.7\.0.+?\r\n'
EON_HU_INSTANTANEOUS_POWER_FACTOR_L1 = r'^\d-\d:33\.7\.0.+?\r\n'
EON_HU_INSTANTANEOUS_POWER_FACTOR_L2 = r'^\d-\d:53\.7\.0.+?\r\n'
EON_HU_INSTANTANEOUS_POWER_FACTOR_L3 = r'^\d-\d:73\.7\.0.+?\r\n'
EON_HU_FREQUENCY = r'^\d-\d:14\.7\.0.+?\r\n'
EON_HU_INSTANTANEOUS_REACTIVE_POWER_Q1 = r'^\d-\d:5\.7\.0.+?\r\n'
EON_HU_INSTANTANEOUS_REACTIVE_POWER_Q2 = r'^\d-\d:6\.7\.0.+?\r\n'
EON_HU_INSTANTANEOUS_REACTIVE_POWER_Q3 = r'^\d-\d:7\.7\.0.+?\r\n'
EON_HU_INSTANTANEOUS_REACTIVE_POWER_Q4 = r'^\d-\d:8\.7\.0.+?\r\n'
