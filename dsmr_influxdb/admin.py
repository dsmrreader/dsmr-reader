from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_influxdb.models import InfluxdbIntegrationSettings


@admin.register(InfluxdbIntegrationSettings)
class InfluxdbIntegrationSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'hostname', 'port', 'secure', 'username', 'password', 'database'],
            }
        ),
        (
            _('Mapping'), {
                'fields': ['formatting'],
                'description': _(
                    '''Example:
<pre>
### [measurement_name]
### DSMR-reader field 1 = InfluxDB field 1
### DSMR-reader field 2 = InfluxDB field 2

[electricity_live]
electricity_currently_delivered = currently_delivered
electricity_currently_returned = currently_returned

[electricity_positions]
electricity_delivered_1 = delivered_1
electricity_returned_1 = returned_1
electricity_delivered_2 = delivered_2
electricity_returned_2 = returned_2

[electricity_voltage]
phase_voltage_l1 = phase_l1
phase_voltage_l2 = phase_l2
phase_voltage_l3 = phase_l3

[electricity_phases]
phase_currently_delivered_l1 = currently_delivered_l1
phase_currently_delivered_l2 = currently_delivered_l2
phase_currently_delivered_l3 = currently_delivered_l3
phase_currently_returned_l1 = currently_returned_l1
phase_currently_returned_l2 = currently_returned_l2
phase_currently_returned_l3 = currently_returned_l3

[electricity_power]
phase_power_current_l1 = current_l1
phase_power_current_l2 = current_l2
phase_power_current_l3 = current_l3

[gas_positions]
extra_device_delivered = delivered
</pre>
'''
                )
            }
        ),
    )
