from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class ConsumptionSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    COMPACTOR_GROUPING_BY_READING = 1
    COMPACTOR_GROUPING_BY_MINUTE = 2
    COMPACTOR_GROUPING_CHOICES = (
        (COMPACTOR_GROUPING_BY_READING, _('By reading (every X seconds)')),
        (COMPACTOR_GROUPING_BY_MINUTE, _('By minute')),
    )

    compactor_grouping_type = models.IntegerField(
        choices=COMPACTOR_GROUPING_CHOICES,
        default=COMPACTOR_GROUPING_BY_MINUTE,
        verbose_name=_('Compactor grouping type'),
        help_text=_('Electricity readings are read every X seconds. We can group those for you.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Consumption configuration')
