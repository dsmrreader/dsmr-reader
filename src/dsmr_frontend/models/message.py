from django.utils.translation import gettext_lazy as _
from django.db import models

from dsmr_backend.mixins import ModelUpdateMixin


class NotificationManager(models.Manager):
    def unread(self):
        return self.get_queryset().filter(read=False)


class Notification(ModelUpdateMixin, models.Model):
    """Used to queue (Dashboard) notification messages to end users."""

    objects = NotificationManager()

    message = models.TextField()  # type: ignore[var-annotated]
    redirect_to = models.CharField(  # type: ignore[var-annotated]  # = a Django reverse URL!
        max_length=64, null=True, blank=True, default=None
    )
    read = models.BooleanField(default=False)  # type: ignore[var-annotated]

    class Meta:
        default_permissions = ("delete",)  # Do allow deletion.
        verbose_name = _("Application notification")
