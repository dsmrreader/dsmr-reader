from django.db import models
from django.utils.translation import ugettext as _
from solo.models import SingletonModel


class FrontendSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    reverse_dashboard_graphs = models.BooleanField(
        default=False,
        verbose_name=_('Reverse dashboard graphs'),
        help_text=_('Whether graphs are rendered with an reversed X-axis')
    )

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Frontend configuration')
