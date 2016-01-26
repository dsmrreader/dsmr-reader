from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models.settings import FrontendSettings


@admin.register(FrontendSettings)
class FrontendSettingsAdmin(SingletonModelAdmin):
    list_display = ('reverse_dashboard_graphs', )
