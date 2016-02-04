from django.contrib import admin

from .models.note import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('day', 'description')
