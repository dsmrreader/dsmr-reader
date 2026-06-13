from django.conf import settings
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django import forms
from solo.admin import SingletonModelAdmin
import django.db.models.signals

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_weather.models.settings import WeatherSettings


class WeatherSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = WeatherSettings
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # When tracking is disabled, get_buienradar_stations() returns [] so the
        # TypedChoiceField has no valid choices. Pin the current station as the
        # sole choice so the form can be saved without an API call.
        is_tracking = (
            bool(self.data.get("track")) if self.data else (self.instance.track if self.instance.pk else False)
        )
        if not is_tracking:
            current = (
                self.instance.buienradar_station
                if self.instance.pk
                else WeatherSettings._meta.get_field("buienradar_station").default
            )
            self.fields["buienradar_station"].choices = [(current, str(current))]


@admin.register(WeatherSettings)
class WeatherSettingsAdmin(SingletonModelAdmin):
    form = WeatherSettingsAdminForm
    fieldsets = (
        (
            None,
            {
                "fields": ["track"],
            },
        ),
        (
            _("Buienradar"),
            {
                "fields": ["buienradar_station"],
                "description": _(
                    'See <a href="https://www.buienradar.nl/nederland/weerbericht/weerstations" target="_blank" '
                    'rel="noopener noreferrer">'
                    "Buienradar weerstations</a> for a map of all locations."
                ),
            },
        ),
    )


@receiver(django.db.models.signals.post_save, sender=WeatherSettings)
def handle_weather_settings_update(sender, instance, **kwargs):
    """Hook to toggle related scheduled process."""
    ScheduledProcess.objects.filter(module=settings.DSMRREADER_MODULE_WEATHER_UPDATE).update(active=instance.track)
