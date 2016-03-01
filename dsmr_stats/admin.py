from django.contrib import admin
from django.forms import widgets
from django.db import models

from .models.note import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('day', 'description')
    formfield_overrides = {
        models.CharField: {'widget': widgets.Textarea},
    }
