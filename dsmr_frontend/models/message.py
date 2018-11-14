from django.utils.translation import ugettext_lazy as _
from django.db import models


class NotificationManager(models.Manager):
    def unread(self):
        return self.get_queryset().filter(read=False)


class Notification(models.Model):
    """ Used to queue messages to end users. """
    objects = NotificationManager()

    message = models.TextField()
    redirect_to = models.CharField(max_length=64, null=True, blank=True, default=None)  # = a Django reverse URL!
    read = models.BooleanField(default=False)

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Application notification')
