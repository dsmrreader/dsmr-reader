from django.contrib import admin
from django.forms import widgets
from django.db import models
from solo.admin import SingletonModelAdmin

from .models.note import Note
from dsmr_stats.models.settings import StatsSettings


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('day', 'description')
    formfield_overrides = {
        models.CharField: {'widget': widgets.Textarea},
    }


@admin.register(StatsSettings)
class StatsSettingsAdmin(SingletonModelAdmin):
    list_display = ('track', )
