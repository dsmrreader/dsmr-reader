from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class FrontendSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    RECENT_HISTORY_RANGE_CHOICES = (
        (1, _('Last week')),
        (2, _('Last two weeks')),
        (3, _('Last three weeks')),
        (4, _('Last four weeks')),
        (5, _('Last five weeks')),
    )

    reverse_dashboard_graphs = models.BooleanField(
        default=False,
        verbose_name=_('Reverse dashboard graphs'),
        help_text=_('Whether graphs are rendered with an reversed X-axis')
    )

    recent_history_weeks = models.IntegerField(
        choices=RECENT_HISTORY_RANGE_CHOICES,
        default=4,
        verbose_name=_('Recent history weeks'),
        help_text=_('The number of weeks displayed in the recent history overview.')
    )

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Frontend configuration')
