from django import forms
from django.utils.translation import ugettext_lazy as _


class ExportAsCsvForm(forms.Form):
    DATA_TYPE_DAY = 'day'
    DATA_TYPE_HOUR = 'hour'
    DATA_TYPES = (
        (DATA_TYPE_DAY, _('Day')),
        (DATA_TYPE_HOUR, _('Hour')),
    )
    EXPORT_FORMAT_CSV = 'csv'
    EXPORT_FORMATS = (
        (EXPORT_FORMAT_CSV, _('CSV')),
    )

    data_type = forms.ChoiceField(choices=DATA_TYPES)
    start_date = forms.DateField()
    end_date = forms.DateField()
    export_format = forms.ChoiceField(choices=EXPORT_FORMATS)


class DashboardGraphForm(forms.Form):
    electricity_offset = forms.IntegerField(required=False)
    gas_offset = forms.IntegerField(required=False)

    def _clean_offset(self, offset_type):
        offset = self.cleaned_data[offset_type]

        if offset is None or offset < 0:
            offset = 0

        return offset

    def clean_electricity_offset(self):
        return self._clean_offset('electricity_offset')

    def clean_gas_offset(self):
        return self._clean_offset('gas_offset')


class DashboardNotificationReadForm(forms.Form):
    notification_id = forms.IntegerField()
