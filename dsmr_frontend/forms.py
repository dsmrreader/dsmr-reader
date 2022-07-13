from django import forms
from django.utils.translation import gettext_lazy as _

import dsmr_backend.services.backend


class ExportAsCsvForm(forms.Form):
    DATA_TYPE_DAY = 'day'
    DATA_TYPE_HOUR = 'hour'
    DATA_TYPE_TEMPERATURE = 'temperature'
    DATA_TYPES = (
        (DATA_TYPE_DAY, _('Day')),
        (DATA_TYPE_HOUR, _('Hour')),
        (DATA_TYPE_TEMPERATURE, _('Temperatures')),
    )
    EXPORT_FORMAT_CSV = 'csv'
    EXPORT_FORMATS = (
        (EXPORT_FORMAT_CSV, _('CSV')),
    )

    data_type = forms.ChoiceField(choices=DATA_TYPES)
    start_date = forms.DateField()
    end_date = forms.DateField()
    export_format = forms.ChoiceField(choices=EXPORT_FORMATS)


class DashboardElectricityConsumptionForm(forms.Form):
    delivered = forms.BooleanField(required=False, initial=False)
    returned = forms.BooleanField(required=False, initial=False)
    total_delivered = forms.BooleanField(required=False, initial=False)
    total_returned = forms.BooleanField(required=False, initial=False)
    phases = forms.BooleanField(required=False, initial=False)
    voltage = forms.BooleanField(required=False, initial=False)
    power_current = forms.BooleanField(required=False, initial=False)
    latest_delta_id = forms.IntegerField(required=False, initial=None)

    def __init__(self, *args, **kwargs):
        self.capabilities = dsmr_backend.services.backend.get_capabilities()
        super(DashboardElectricityConsumptionForm, self).__init__(*args, **kwargs)

    def _clean_type(self, field, capability):
        value = self.cleaned_data[field]

        if value and not self.capabilities[capability]:
            raise forms.ValidationError('Capability not enabled: {}'.format(capability))

        return value

    def clean_delivered(self):
        return self._clean_type('delivered', 'electricity')

    def clean_returned(self):
        return self._clean_type('returned', 'electricity_returned')

    def clean_total_delivered(self):
        return self._clean_type('total_delivered', 'electricity')

    def clean_total_returned(self):
        return self._clean_type('total_returned', 'electricity_returned')

    def clean_phases(self):
        return self._clean_type('phases', 'multi_phases')

    def clean_voltage(self):
        return self._clean_type('voltage', 'voltage')

    def clean_power_current(self):
        return self._clean_type('power_current', 'power_current')


class NotificationReadForm(forms.Form):
    notification_id = forms.IntegerField()


class TrendsPeriodForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()

    def clean(self):
        if self.cleaned_data.get('start_date') \
                and self.cleaned_data.get('end_date') \
                and self.cleaned_data.get('start_date') > self.cleaned_data.get('end_date'):
            raise forms.ValidationError(_('Selected date range START cannot be AFTER selected date range END'))

        return super().clean()
