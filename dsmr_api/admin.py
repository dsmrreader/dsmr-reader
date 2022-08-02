from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import APISettings


@admin.register(APISettings)
class APISettingsAdmin(SingletonModelAdmin):
    change_form_template = "dsmr_api/api_settings/change_form.html"
