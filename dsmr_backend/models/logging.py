import logging

from django.utils.translation import gettext_lazy as _
from django.db import models


class LoggingRecord(models.Model):
    LEVEL_CHOICES = (
        (logging.getLevelName(logging.WARNING), logging.getLevelName(logging.WARNING)),
        (logging.getLevelName(logging.ERROR), logging.getLevelName(logging.ERROR)),
        (logging.getLevelName(logging.CRITICAL), logging.getLevelName(logging.CRITICAL)),
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True
    )
    level = models.CharField(
        choices=LEVEL_CHOICES,
        max_length=8,
        verbose_name=_('Log level'),
        help_text=_('The log level of this message'),
    )
    message = models.TextField(
        verbose_name=_('Message'),
    )

    class Meta:
        default_permissions = tuple()
        ordering = ['-pk']
        verbose_name = _('Logging record')
        verbose_name_plural = _('Logging records')
