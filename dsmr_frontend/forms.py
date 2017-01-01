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
    units_offset = forms.IntegerField(required=False)

    def clean_units_offset(self):
        units_offset = self.cleaned_data['units_offset']

        if units_offset is None or units_offset < 0:
            units_offset = 0

        return units_offset


class DashboardNotificationReadForm(forms.Form):
    notification_id = forms.IntegerField()
