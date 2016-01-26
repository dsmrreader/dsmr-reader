from django.db import models
from django.utils.translation import ugettext as _
from solo.models import SingletonModel


class DataloggerSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    baud_rate = models.IntegerField(
        default=115200,
        verbose_name=_('BAUD rate'),
        help_text=_('BAUD rate used for Smartmeter. 115200 for DSMR v4, 9600 for older versions')
    )

    com_port = models.CharField(
        max_length=196,
        default='/dev/ttyUSB0',
        verbose_name=_('COM-port'),
        help_text=_('COM-port connected to Smartmeter.')
    )

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Datalogger configuration')
