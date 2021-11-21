from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_backend.mixins import DeletionOnlyAdminModel
from dsmr_influxdb.models import InfluxdbIntegrationSettings, InfluxdbMeasurement


@admin.register(InfluxdbIntegrationSettings)
class InfluxdbIntegrationSettingsAdmin(SingletonModelAdmin):
    change_form_template = 'dsmr_influxdb/influxdb_settings/change_form.html'
    fieldsets = (
        (
            None, {
                'fields': [
                    'enabled', 'hostname', 'port', 'secure', 'organization', 'api_token', 'bucket',
                ],
                'description': _(
                    'The backend process should automatically restart to apply changes.'
                )
            }
        ),
        (
            _('Mapping'), {
                'fields': ['formatting'],
                'description':
                    '''Example:
<pre>
### [measurement_name]
### DSMR reading field 1 = InfluxDB field 1
### DSMR reading field 2 = InfluxDB field 2
### Only DSMR reading fields are supported

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

            }
        ),
    )


@admin.register(InfluxdbMeasurement)
class InfluxdbMeasurementAdmin(DeletionOnlyAdminModel):
    list_display = ('time', 'measurement_name')
