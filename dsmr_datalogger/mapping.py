from dsmr_parser import obis_references


DSMR_MAPPING = {
    # Data stored in database for every reading.
    obis_references.P1_MESSAGE_TIMESTAMP: 'timestamp',
    obis_references.ELECTRICITY_USED_TARIFF_1: 'electricity_delivered_1',
    obis_references.ELECTRICITY_DELIVERED_TARIFF_1: 'electricity_returned_1',
    obis_references.ELECTRICITY_USED_TARIFF_2: 'electricity_delivered_2',
    obis_references.ELECTRICITY_DELIVERED_TARIFF_2: 'electricity_returned_2',
    obis_references.CURRENT_ELECTRICITY_USAGE: 'electricity_currently_delivered',
    obis_references.CURRENT_ELECTRICITY_DELIVERY: 'electricity_currently_returned',

    obis_references.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE: 'phase_currently_delivered_l1',
    obis_references.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE: 'phase_currently_delivered_l2',
    obis_references.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE: 'phase_currently_delivered_l3',
    obis_references.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE: 'phase_currently_returned_l1',
    obis_references.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE: 'phase_currently_returned_l2',
    obis_references.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE: 'phase_currently_returned_l3',
    obis_references.INSTANTANEOUS_VOLTAGE_L1: 'phase_voltage_l1',
    obis_references.INSTANTANEOUS_VOLTAGE_L2: 'phase_voltage_l2',
    obis_references.INSTANTANEOUS_VOLTAGE_L3: 'phase_voltage_l3',

    # For some reason this identifier contains two fields, therefor we split them.
    obis_references.HOURLY_GAS_METER_READING: {
        'value': 'extra_device_delivered',
        'datetime': 'extra_device_timestamp',
    },
    obis_references.GAS_METER_READING: {  # Legacy
        'value': 'extra_device_delivered',
        'datetime': 'extra_device_timestamp',
    },

    # Static data, stored in database but only record of the last reading is preserved.
    obis_references.P1_MESSAGE_HEADER: 'dsmr_version',
    obis_references.ELECTRICITY_ACTIVE_TARIFF: 'electricity_tariff',
    obis_references.SHORT_POWER_FAILURE_COUNT: 'power_failure_count',
    obis_references.LONG_POWER_FAILURE_COUNT: 'long_power_failure_count',
    obis_references.VOLTAGE_SAG_L1_COUNT: 'voltage_sag_count_l1',
    obis_references.VOLTAGE_SAG_L2_COUNT: 'voltage_sag_count_l2',
    obis_references.VOLTAGE_SAG_L3_COUNT: 'voltage_sag_count_l3',
    obis_references.VOLTAGE_SWELL_L1_COUNT: 'voltage_swell_count_l1',
    obis_references.VOLTAGE_SWELL_L2_COUNT: 'voltage_swell_count_l2',
    obis_references.VOLTAGE_SWELL_L3_COUNT: 'voltage_swell_count_l3',
}
