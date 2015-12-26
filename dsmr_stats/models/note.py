from django.db import models
from django.utils.translation import ugettext as _


class Note(models.Model):
    """ Daily note someone might place for some remarks about something related to consumption. """
    day = models.DateField()
    description = models.CharField(max_length=256)

    class Meta:
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')

    def __str__(self):
        return '{} | {} ({})'.format(self.__class__.__name__, self.description, self.day)
