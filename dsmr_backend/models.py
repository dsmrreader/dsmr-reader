import importlib

from django.utils.translation import ugettext as _
from django.utils import timezone
from django.db import models

from dsmr_backend.exceptions import DelayNextCall


class ScheduledCallManager(models.Manager):
    def callable(self):
        """ Returns any instances that can be called. """
        return self.get_queryset().filter(
            next_call__lte=timezone.now()
        )


class ScheduledCall(models.Model):
    """ Represents a call scheduled for execution. Keeps track when it should be called again. """
    objects = ScheduledCallManager()

    name = models.CharField(max_length=64)
    module_path = models.CharField(
        db_index=True,
        unique=True,
        max_length=128
    )
    next_call = models.DateTimeField(
        db_index=True,
        auto_now_add=True,
        help_text=_("Timestamp indicating the next execution for this call")
    )

    def execute(self):
        # Import the first part of the path, execute the last bit later.
        splitted_path = self.module_path.split('.')
        import_path = '.'.join(splitted_path[:-1])
        call_path = splitted_path[-1]

        imported_module = importlib.import_module(name=import_path)
        service = getattr(imported_module, call_path)

        try:
            return service()
        except DelayNextCall as ex:
            self.delay(ex.delta)

    def delay(self, delta):
        """ Delays the next call by the given delta. """
        self.next_call = timezone.now() + delta
        self.save(update_fields=['next_call'])

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Scheduled call (read only)')
        verbose_name_plural = _('Scheduled calls (read only)')

    def __str__(self):
        return self.name
