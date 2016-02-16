from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class StatsSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    track = models.BooleanField(
        default=True,
        verbose_name=_('Track trends'),
        help_text=_(
            'Whether we should track trends by storing daily consumption summaries.'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Trends & statistics configuration')
