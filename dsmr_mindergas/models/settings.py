from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class MinderGasSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    API_URL = 'https://www.mindergas.nl/api/gas_meter_readings'

    export = models.BooleanField(
        default=False,
        verbose_name=_('Export data to MinderGas'),
        help_text=_(
            'Whether we should export your gas readings (if any) to your MinderGas.nl account.'
        )
    )
    auth_token = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default=None,
        verbose_name=_('MinderGas authentication token'),
        help_text=_(
            'The authentication token used to authenticate for the MinderGas API. '
            'More information can be found here: https://www.mindergas.nl/member/api'
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
        verbose_name = _('MinderGas.nl configuration')
