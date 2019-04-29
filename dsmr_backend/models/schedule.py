import importlib
import logging

from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models


logger = logging.getLogger('commands')


class ScheduledProcessManager(models.Manager):
    def ready(self):
        return self.get_queryset().filter(planned__lte=timezone.now())


class ScheduledProcess(models.Model):
    """ A scheduled process, not to be executed before the planned moment. """
    objects = ScheduledProcessManager()
    name = models.CharField(max_length=64)
    module = models.CharField(max_length=128, unique=True)
    planned = models.DateTimeField(default=timezone.now)

    def execute(self):
        # Import the first part of the path, execute the last bit later.
        splitted_path = self.module.split('.')
        import_path = '.'.join(splitted_path[:-1])
        call_path = splitted_path[-1]

        imported_module = importlib.import_module(name=import_path)
        service = getattr(imported_module, call_path)
        return service(self)

    def delay(self, delta):
        """ Delays the next call by the given delta. """
        logger.debug('Rescheduling %s with: %s', self.module, delta)
        self.planned = timezone.now() + delta
        self.save(update_fields=['planned'])

    def __str__(self):
        return self.name

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Scheduled process')
