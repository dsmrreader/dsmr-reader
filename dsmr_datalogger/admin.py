from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models.settings import DataloggerSettings


@admin.register(DataloggerSettings)
class DataloggerSettingsAdmin(SingletonModelAdmin):
    list_display = ('com_port', )
