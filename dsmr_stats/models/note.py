from django.db import models
from django.utils.translation import ugettext_lazy as _


class Note(models.Model):
    """ Daily note someone might place for some remarks about something related to consumption. """
    day = models.DateField(db_index=True, verbose_name=_('Day'))
    description = models.CharField(max_length=256, verbose_name=_('Description'))

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')

    def __str__(self):
        return '{} | {} ({})'.format(self.__class__.__name__, self.description, self.day)
