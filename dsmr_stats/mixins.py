from collections import defaultdict
import json

from django.conf import settings
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_stats.models.statistics import ElectricityStatistics
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_stats.models.settings import StatsSettings
from dsmr_weather.models.statistics import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
import dsmr_stats.services


class DashboardMixin(object):
    electricity_max = 60
    gas_max = 3 * 24
    temperature_max = gas_max

    def get_context_data(self, **kwargs):
        stats_settings = StatsSettings.get_solo()
        context_data = super(DashboardMixin, self).get_context_data(**kwargs)

        electricity = ElectricityConsumption.objects.all().order_by('read_at')
        gas = GasConsumption.objects.all().order_by('read_at')
        temperature = TemperatureReading.objects.all().order_by('read_at')

        # User might want to sort things backwards.
        if stats_settings.reverse_dashboard_graphs:
            electricity = electricity.reverse()[:self.electricity_max]
            gas = gas.reverse()[:self.gas_max]
            temperature = temperature.reverse()[:self.temperature_max]
        else:
            # We can't slice using negative offsets, so we should fetch a (quick) count first)
            electricity_offset = max(0, electricity.count() - self.electricity_max)
            gas_offset = max(0, gas.count() - self.gas_max)
            temperature_offset = max(0, temperature.count() - self.temperature_max)

            electricity = electricity[electricity_offset:]
            gas = gas[gas_offset:]
            temperature = temperature[temperature_offset:]

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

        latest_electricity = ElectricityConsumption.objects.all().order_by('-read_at')[0]
        latest_gas = GasConsumption.objects.all().order_by('-read_at')[0]

        context_data['latest_electricity_read'] = latest_electricity.read_at
        context_data['latest_electricity'] = int(
            latest_electricity.currently_delivered * 1000
        )
        context_data['latest_electricity_returned'] = int(
            latest_electricity.currently_returned * 1000
        )

        context_data['latest_gas_read'] = latest_gas.read_at
        context_data['latest_gas'] = latest_gas.currently_delivered

        try:
            context_data['consumption'] = dsmr_stats.services.day_consumption(
                day=latest_electricity.read_at.astimezone(settings.LOCAL_TIME_ZONE)
            )
        except LookupError:
            pass

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
            now - timezone.timedelta(days=n) for n in reversed(range(
                self.days_offset, self.days_ago + 1
            ))
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
        context_data['dsmr_stats'] = ElectricityStatistics.objects.all().order_by('-pk')[0]
        context_data['total_reading_count'] = DsmrReading.objects.count()
        context_data['first_reading'] = DsmrReading.objects.all().order_by('pk')[0].timestamp
        context_data['last_reading'] = DsmrReading.objects.all().order_by('-pk')[0].timestamp

        try:
            context_data['consumption'] = dsmr_stats.services.day_consumption(
                day=timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
            )
        except LookupError:
            pass

        return context_data
