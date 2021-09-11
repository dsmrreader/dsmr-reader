from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.forms import widgets
from django.db import models
from solo.admin import SingletonModelAdmin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from .models.note import Note
from .models.statistics import HourStatistics, DayStatistics, ElectricityStatistics


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
class DayStatisticsAdmin(admin.ModelAdmin):
    actions = None
    ordering = ['-day', 'total_cost']
    list_display = ('day', 'electricity_merged', 'electricity_returned_merged', 'fixed_cost', 'total_cost')
    list_filter = (
        ('day', DateRangeFilter),
    )
    fieldsets = (
        (
            None, {
                'fields': ['day'],
            }
        ),
        (
            _('Diff'), {
                'fields': ['electricity1', 'electricity2', 'electricity1_returned', 'electricity2_returned', 'gas'],
            }
        ),
        (
            _('Readings'), {
                'fields': ['electricity1_reading', 'electricity2_reading', 'electricity1_returned_reading',
                           'electricity2_returned_reading', 'gas_reading'],
            }
        ),
        (
            _('Costs'), {
                'fields': ['electricity1_cost', 'electricity2_cost', 'gas_cost', 'fixed_cost', 'total_cost'],
            }
        ),
        (
            _('Weather'), {
                'fields': ['lowest_temperature', 'highest_temperature', 'average_temperature'],
            }
        ),
    )


@admin.register(HourStatistics)
class HourStatisticsAdmin(admin.ModelAdmin):
    actions = None
    ordering = ['-hour_start']
    list_display = (
        'hour_start', 'formatted_electricity_merged', 'formatted_electricity_returned_merged', 'formatted_gas'
    )
    list_filter = (
        ('hour_start', DateTimeRangeFilter),
    )

    def formatted_electricity_merged(self, obj: HourStatistics) -> str:
        if not obj.electricity_merged:
            return '-'

        return obj.electricity_merged
    formatted_electricity_merged.short_description = 'electricity delivered'

    def formatted_electricity_returned_merged(self, obj: HourStatistics) -> str:
        if not obj.electricity_returned_merged:
            return '-'

        return obj.electricity_returned_merged
    formatted_electricity_returned_merged.short_description = 'electricity returned'

    def formatted_gas(self, obj: HourStatistics) -> str:
        if not obj.gas:
            return '-'

        return obj.gas
    formatted_gas.short_description = 'gas'


@admin.register(ElectricityStatistics)
class ElectricityStatisticsAdmin(SingletonModelAdmin):
    actions = None
