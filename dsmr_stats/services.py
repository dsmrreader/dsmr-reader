def create_daily_statistics(day):
    pass
#     # The last thing to do is to keep track of other daily statistics.
#     electricity_statistics = ElectricityStatistics(
#         day=dsmr_reading.timestamp.date(),
#         power_failure_count=dsmr_reading.power_failure_count,
#         long_power_failure_count=dsmr_reading.long_power_failure_count,
#         voltage_sag_count_l1=dsmr_reading.voltage_sag_count_l1,
#         voltage_sag_count_l2=dsmr_reading.voltage_sag_count_l2,
#         voltage_sag_count_l3=dsmr_reading.voltage_sag_count_l3,
#         voltage_swell_count_l1=dsmr_reading.voltage_swell_count_l1,
#         voltage_swell_count_l2=dsmr_reading.voltage_swell_count_l2,
#         voltage_swell_count_l3=dsmr_reading.voltage_swell_count_l3,
#     )
# 
#     try:
#         existing_statistics = ElectricityStatistics.objects.get(
#             day=electricity_statistics.day
#         )
#     except ElectricityStatistics.DoesNotExist:
#         # This will succeed once every day.
#         statistics = electricity_statistics.save()
# 
#         dsmr_consumption.signals.electricity_statistics_created.send_robust(
#             None, instance=statistics
#         )
#     else:
#         # Already exists, but only save if dirty.
#         if not existing_statistics.is_equal(electricity_statistics):
#             electricity_statistics.id = existing_statistics.id
#             electricity_statistics.pk = existing_statistics.pk
#             electricity_statistics.save()
