from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models.settings import ConsumptionSettings


@admin.register(ConsumptionSettings)
class ConsumptionSettingsAdmin(SingletonModelAdmin):
    list_display = ('compactor_grouping_type', )
