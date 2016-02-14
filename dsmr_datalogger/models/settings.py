from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class DataloggerSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    DSMR_VERSION_4 = 4
    DSMR_VERSION_3 = 3
    DSMR_VERSION_CHOICES = (
        (DSMR_VERSION_4, _('DSMR version 4')),
        (DSMR_VERSION_3, _('DSMR version 2/3')),
    )

    track = models.BooleanField(
        default=True,
        verbose_name=_('Poll P1 port'),
        help_text=_(
            'Whether we should track the P1 port on your smartmeter. Almost every feature inside '
            'this project requires this to be enabled. However, it might be disabled temporarily '
            'due to technical reasons, such as data migrations.'
        )
    )
    track_meter_statistics = models.BooleanField(
        default=True,
        verbose_name=_('Track meter statistics'),
        help_text=_(
            'Whether we should track any extra statistics sent by the meter, such as the number of '
            'power failures of voltage dips. Data is not required for core features.'
        )
    )

    dsmr_version = models.IntegerField(
        default=DSMR_VERSION_4,
        choices=DSMR_VERSION_CHOICES,
        verbose_name=_('DSMR version'),
        help_text=_('The DSMR version your meter supports. Version should be printed on meter.')
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
