from django.contrib import admin

from solo.admin import SingletonModelAdmin

from dsmr_mindergas.models.settings import MinderGasSettings


@admin.register(MinderGasSettings)
class MinderGasSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('next_export', )
