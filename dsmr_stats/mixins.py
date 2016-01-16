from collections import defaultdict
import json

from django.conf import settings
from django.utils import timezone

from dsmr_stats import models as stats_models
from dsmr_weather.models.statistics import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
import dsmr_stats.services


class DashboardMixin(object):
    electricity_readings = 60
    gas_readings = 3 * 24
    temperature_readings = gas_readings

    def get_context_data(self, **kwargs):
        context_data = super(DashboardMixin, self).get_context_data(**kwargs)
        electricity = stats_models.ElectricityConsumption.objects.all().order_by(
            "-read_at"
        )[0:self.electricity_readings]
        gas = stats_models.GasConsumption.objects.all().order_by(
            "-read_at"
        )[0:self.gas_readings]
        temperature = TemperatureReading.objects.all().order_by(
            "-read_at"
        )[0:self.temperature_readings]

        context_data['electricity_x'] = json.dumps(
            [x.read_at.astimezone(
                settings.LOCAL_TIME_ZONE
            ).strftime("%a %H:%M") for x in electricity]
        )
        context_data['electricity_y'] = json.dumps(
            [float(x.currently_delivered * 1000) for x in electricity]
        )

        context_data['gas_x'] = json.dumps(
            [x.read_at.astimezone(
                settings.LOCAL_TIME_ZONE
            ).strftime("%a %H:%M") for x in gas]
        )
        context_data['gas_y'] = json.dumps(
            [float(x.currently_delivered) for x in gas]
        )

        context_data['track_temperature'] = WeatherSettings.get_solo().track

        if context_data['track_temperature']:
            context_data['temperature_x'] = json.dumps(
                [x.read_at.astimezone(
                    settings.LOCAL_TIME_ZONE
                ).strftime("%a %H:%M") for x in temperature]
            )
            context_data['temperature_y'] = json.dumps(
                [float(x.degrees_celcius) for x in temperature]
            )

        latest_electricity = electricity[0]
        context_data['latest_electricity_read'] = latest_electricity.read_at
        context_data['latest_electricity'] = int(
            latest_electricity.currently_delivered * 1000
        )
        context_data['latest_electricity_returned'] = int(
            latest_electricity.currently_returned * 1000
        )

        latest_gas = gas[0]
        context_data['latest_gas_read'] = latest_gas.read_at
        context_data['latest_gas'] = latest_gas.currently_delivered

        try:
            context_data['consumption'] = dsmr_stats.services.day_consumption(
                day=latest_electricity.read_at.astimezone(settings.LOCAL_TIME_ZONE)
            )
        except LookupError:
            pass

        return context_data


class ArchiveMixin(object):
    def get_context_data(self, **kwargs):
        context_data = super(ArchiveMixin, self).get_context_data(**kwargs)
        ec = stats_models.ElectricityConsumption.objects.all().order_by('read_at')[0]
        daterangepicker_format = '%d-%m-%Y'
        context_data['start_date'] = ec.read_at.astimezone(
            settings.LOCAL_TIME_ZONE
        ).strftime(daterangepicker_format)
        context_data['end_date'] = timezone.now().astimezone(
            settings.LOCAL_TIME_ZONE
        ).strftime(daterangepicker_format)
        return context_data


class HistoryMixin(object):
    days_ago = 28
    days_offset = 1

    def get_context_data(self, **kwargs):
        context_data = super(HistoryMixin, self).get_context_data(**kwargs)
        context_data['usage'] = []
        context_data['days_ago'] = self.days_ago
        context_data['track_temperature'] = WeatherSettings.get_solo().track

        # @TODO: There must be a way to make this more clean.
        context_data['chart'] = defaultdict(list)
        CONSUMPTION_FIELDS = (
            'electricity1_cost', 'electricity2_cost', 'gas_cost', 'total_cost',
            'gas', 'electricity1', 'electricity2', 'electricity1_returned',
            'electricity2_returned', 'average_temperature'
        )

        # Summarize stats for the past two weeks.
        now = timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
        dates = (
            now - timezone.timedelta(days=n) for n in range(
                self.days_offset, self.days_ago + 1
            )
        )

        for current_day in dates:
            current_day = current_day.astimezone(settings.LOCAL_TIME_ZONE)

            try:
                day_consumption = dsmr_stats.services.day_consumption(
                    day=current_day
                )
            except LookupError:
                continue

            context_data['usage'].append(day_consumption)
            context_data['chart']['days'].append(current_day.strftime("%a %d-%m"))

            for current_field in CONSUMPTION_FIELDS:
                context_data['chart'][current_field].append(float(
                    day_consumption[current_field]
                ))

        for key, value in context_data['chart'].items():
            context_data['chart'][key] = json.dumps(value)

        return context_data


class StatisticsMixin(object):
    def get_context_data(self, **kwargs):
        context_data = super(StatisticsMixin, self).get_context_data(**kwargs)
        context_data['dsmr_stats'] = stats_models.ElectricityStatistics.objects.all().order_by('-pk')[0]
        context_data['total_reading_count'] = stats_models.DsmrReading.objects.count()
        context_data['first_reading'] = stats_models.DsmrReading.objects.all().order_by('pk')[0].timestamp
        context_data['last_reading'] = stats_models.DsmrReading.objects.all().order_by('-pk')[0].timestamp

        try:
            context_data['consumption'] = dsmr_stats.services.day_consumption(
                day=timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
            )
        except LookupError:
            pass

        return context_data
