from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class ContinuousClientSettings(ModelUpdateMixin, SingletonModel):
    """ Settings for the dsmr_client process. """
    restart_required = models.BooleanField(
        default=False,
        verbose_name=_('Restart required'),
        help_text=_('Whether the process requires a restart, forcing all continuous clients to reset and reconnect.')
    )
    process_sleep = models.DecimalField(
        default=1,
        max_digits=3,
        decimal_places=1,
        verbose_name=_('Process sleep'),
        help_text=_(
            'The number of seconds the process sleeps after completing a run.'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Client process settings')
