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

    def get_form(self, request, obj=None, **kwargs):
        form = super(NoteAdmin, self).get_form(request, obj, **kwargs)
        day = request.GET.get('day')

        if day:
            form.base_fields['day'].initial = day

        return form
