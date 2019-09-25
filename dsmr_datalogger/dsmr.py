DSMR_MAPPING = {
    # Data stored in database for every reading.
    '0-0:1.0.0': 'timestamp',
    '1-0:1.8.1': 'electricity_delivered_1',
    '1-0:2.8.1': 'electricity_returned_1',
    '1-0:1.8.2': 'electricity_delivered_2',
    '1-0:2.8.2': 'electricity_returned_2',
    '1-0:1.7.0': 'electricity_currently_delivered',
    '1-0:2.7.0': 'electricity_currently_returned',

    '1-0:21.7.0': 'phase_currently_delivered_l1',
    '1-0:41.7.0': 'phase_currently_delivered_l2',
    '1-0:61.7.0': 'phase_currently_delivered_l3',
    '1-0:22.7.0': 'phase_currently_returned_l1',
    '1-0:42.7.0': 'phase_currently_returned_l2',
    '1-0:62.7.0': 'phase_currently_returned_l3',
    '1-0:32.7.0': 'phase_voltage_l1',
    '1-0:52.7.0': 'phase_voltage_l2',
    '1-0:72.7.0': 'phase_voltage_l3',

    # For some reason this identifier contains two fields, therefor we split them.
    '0-1:24.2.1': ('extra_device_timestamp', 'extra_device_delivered'),

    # Static data, stored in database but only record of the last reading is preserved.
    '1-3:0.2.8': 'dsmr_version',
    '0-0:96.14.0': 'electricity_tariff',
    '0-0:96.7.21': 'power_failure_count',
    '0-0:96.7.9': 'long_power_failure_count',
    '1-0:32.32.0': 'voltage_sag_count_l1',
    '1-0:52.32.0': 'voltage_sag_count_l2',
    '1-0:72.32.0': 'voltage_sag_count_l3',
    '1-0:32.36.0': 'voltage_swell_count_l1',
    '1-0:52.36.0': 'voltage_swell_count_l2',
    '1-0:72.36.0': 'voltage_swell_count_l3',
}
