from typing import ClassVar
from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class APISettings(ModelUpdateMixin, SingletonModel):
    """Singleton model restricted by django-solo plugin. Settings for this application only."""

    allow = models.BooleanField(  # type: ignore[var-annotated]
        default=False,
        verbose_name=_("Enable DSMR-reader API"),
        help_text=_("When disabled it will reject incoming requests and return an HTTP 403 error"),
    )
    auth_key = models.CharField(  # type: ignore[var-annotated]
        max_length=256,
        null=True,
        default=None,
        verbose_name=_("Auth Key"),
        help_text=_("The auth key used to authenticate for this API."),
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions: ClassVar[tuple[str, ...]] = tuple()
        verbose_name = _("API configuration")
