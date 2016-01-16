from django.db import models
from django.utils.translation import ugettext as _
from solo.models import SingletonModel


class StatsSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    COMPACTOR_GROUPING_BY_READING = 1
    COMPACTOR_GROUPING_BY_MINUTE = 2
    COMPACTOR_GROUPING_CHOICES = (
        (COMPACTOR_GROUPING_BY_READING, _('By reading (every 10 seconds)')),
        (COMPACTOR_GROUPING_BY_MINUTE, _('By minute')),
    )

    compactor_grouping_type = models.IntegerField(
        choices=COMPACTOR_GROUPING_CHOICES,
        default=COMPACTOR_GROUPING_BY_MINUTE,
        verbose_name=_('Compactor grouping type'),
        help_text=_('Electricity readings are read every 10 seconds. We can group those for you.')
    )
    reverse_dashboard_graphs = models.BooleanField(
        default=False,
        verbose_name=_('Reverse dashboard graphs'),
        help_text=_('Whether graphs are rendered with an reversed X-axis')
    )

    class Meta:
        verbose_name = _('Stats configuration')
