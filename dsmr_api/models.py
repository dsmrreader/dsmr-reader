from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class APISettings(ModelUpdateMixin, SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    allow = models.BooleanField(
        default=False,
        verbose_name=_('Allow API calls'),
        help_text=_('Whether the API is available for use.')
    )
    auth_key = models.CharField(
        max_length=256,
        null=True,
        default=None,
        verbose_name=_('Auth Key'),
        help_text=_('The auth key used to authenticate for this API.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('API configuration')
