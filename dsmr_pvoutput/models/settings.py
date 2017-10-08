from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from solo.models import SingletonModel


class PVOutputAPISettings(SingletonModel):
    auth_token = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        default=None,
        verbose_name=_('API key'),
        help_text=_('The API key for your PVOutput account. Listed in PVOutput at Settings -> "API Settings".')
    )
    system_identifier = models.CharField(
        null=True,
        blank=True,
        default=None,
        max_length=32,
        verbose_name=_('System ID (digit)'),
        help_text=_('The "System ID" for your device. Listed in PVOutput at Settings -> "Registered Systems".')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('PVOutput: API configuration')


class PVOutputAddStatusSettings(SingletonModel):
    """ API Docs: https://pvoutput.org/help.html#api-addstatus """
    API_URL = 'https://pvoutput.org/service/r2/addstatus.jsp'

    INTERVAL_5_MINUTES = 5
    INTERVAL_10_MINUTES = 10
    INTERVAL_15_MINUTES = 15
    INTERVAL_CHOICES = (
        (INTERVAL_5_MINUTES, _('5 minutes')),
        (INTERVAL_10_MINUTES, _('10 minutes')),
        (INTERVAL_15_MINUTES, _('15 minutes')),
    )

    export = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether the system uploads consumption using the Add Status Service API call.')
    )
    upload_interval = models.IntegerField(
        default=INTERVAL_5_MINUTES,
        choices=INTERVAL_CHOICES,
        verbose_name=_('Upload interval'),
        help_text=_('The interval between each upload (in minutes). Please make sure this matches the device settings.')
    )
    upload_delay = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        verbose_name=_('Upload delay (minutes)'),
        help_text=_(
            'An artificial delay in uploading data to PVOutput. E.g.: When you set this to "5" and the application '
            'uploads the data at 10:45, then only data between 0:00 and 10:40 will be taken into account for upload at '
            'that moment. It effectively limits its upload data search by "X minutes ago".'
        )
    )
    processing_delay = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        verbose_name=_('PVOutput: Processing delay (minutes)'),
        help_text=_(
            '[!]: This feature is ONLY available when you have a DONATOR account for PVOutput.org! Leave EMPTY to '
            'disable the feature. This parameter allows the processing of the data to be delayed, by the specified '
            'number of minutes. Allowed values: empty or 0 to 120 (minutes)'
        )
    )
    next_export = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Next export'),
        help_text=_(
            'Timestamp of the next export. Automatically updated by application.'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('PVOutput: Add Status configuration')
