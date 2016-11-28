from django.contrib.admin.filters import DateFieldListFilter
from django.contrib import admin
from django.forms import widgets
from django.db import models

from dsmr_backend.mixins import ReadOnlyAdminModel
from .models.note import Note
from .models.statistics import HourStatistics, DayStatistics


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('day', 'description')
    formfield_overrides = {
        models.CharField: {'widget': widgets.Textarea},
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super(NoteAdmin, self).get_form(request, obj, **kwargs)
        day = request.GET.get('day')

        if day:
            form.base_fields['day'].initial = day

        return form


@admin.register(DayStatistics)
class DayStatisticsAdmin(ReadOnlyAdminModel):
    """ Read only model. """
    ordering = ['-day']
    list_display = ('day', 'electricity_merged', 'electricity_returned_merged', 'total_cost')
    list_filter = (
        ('day', DateFieldListFilter),
    )


@admin.register(HourStatistics)
class HourStatisticsAdmin(ReadOnlyAdminModel):
    """ Read only model. """
    ordering = ['-hour_start']
    list_display = ('hour_start', 'electricity_merged', 'electricity_returned_merged')
    list_filter = (
        ('hour_start', DateFieldListFilter),
    )
