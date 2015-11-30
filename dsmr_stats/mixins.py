from collections import defaultdict
import json

from django.conf import settings
from django.utils import timezone

from dsmr_stats import models
import dsmr_stats.services


class DashboardMixin(object):
    electricity_readings = 60
    gas_readings = 3 * 24

    def get_context_data(self, **kwargs):
        context_data = super(DashboardMixin, self).get_context_data(**kwargs)
        electricity = models.ElectricityConsumption.objects.all().order_by(
            "-read_at"
        )[0:self.electricity_readings]
        gas = models.GasConsumption.objects.all().order_by(
            "-read_at"
        )[0:self.gas_readings]

        context_data['electricity_x'] = json.dumps(
            [x.read_at.strftime("%a %d-%m") for x in electricity]
        )
        context_data['electricity_y'] = json.dumps(
            [float(x.currently_delivered * 1000) for x in electricity]
        )
        context_data['gas_x'] = json.dumps(
            [x.read_at.strftime("%a %d-%m") for x in gas]
        )
        context_data['gas_y'] = json.dumps(
            [float(x.currently_delivered) for x in gas]
        )
        context_data['latest_electricity'] = int(
            electricity[0].currently_delivered * 1000
        )
        context_data['latest_gas'] = gas[0].currently_delivered
        return context_data


class HistoryMixin(object):
    days_ago = 28
    days_offset = 1

    def get_context_data(self, **kwargs):
        context_data = super(HistoryMixin, self).get_context_data(**kwargs)
        context_data['usage'] = []
        context_data['days_ago'] = self.days_ago

        # @TODO: There must be a way to make this more clean.
        context_data['chart'] = defaultdict(list)
        CONSUMPTION_FIELDS = (
            'electricity1_cost', 'electricity2_cost', 'gas_cost', 'total_cost',
            'gas', 'electricity1', 'electricity2', 'electricity1_returned',
            'electricity2_returned'
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
        context_data['dsmr_stats'] = models.ElectricityStatistics.objects.all().order_by('-pk')[0]
        context_data['total_reading_count'] = models.DsmrReading.objects.count()
        context_data['first_reading'] = models.DsmrReading.objects.all().order_by('pk')[0].timestamp
        context_data['last_reading'] = models.DsmrReading.objects.all().order_by('-pk')[0].timestamp

        try:
            context_data['consumption'] = dsmr_stats.services.day_consumption(
                day=timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
            )
        except LookupError:
            pass

        return context_data


class EnergySupplierPricesMixin(object):
    def get_context_data(self, **kwargs):
        context_data = super(EnergySupplierPricesMixin, self).get_context_data(**kwargs)
        context_data['prices'] = models.EnergySupplierPrice.objects.all()
        return context_data
