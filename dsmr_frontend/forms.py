from django import forms
from django.utils.translation import ugettext_lazy as _


class ExportForm(forms.Form):
    DATA_TYPE_DSMR_READINGS = 'dsmr-readings'
    DATA_TYPE_DAILY_STATISTICS = 'daily-statistics'
    DATA_TYPE_HOURLY_STATISTICS = 'hourly-statistics'

    DATA_TYPES = (
        (DATA_TYPE_DSMR_READINGS, _('DSMR readings')),
        (DATA_TYPE_DAILY_STATISTICS, _('Daily statistics')),
        (DATA_TYPE_HOURLY_STATISTICS, _('Hourly statistics')),
    )

    data_type = forms.ChoiceField(
        label=_('Data type'), choices=DATA_TYPES, initial=DATA_TYPE_DAILY_STATISTICS,
        widget=forms.widgets.RadioSelect(attrs={'class': 'form-control'})
    )
    start = forms.DateField(label=_('Start'))
    end = forms.DateField(label=_('End'))
