from unittest import mock
import random
import json

from django.test import TestCase, Client
from django.utils import timezone
from django.core.urlresolvers import reverse

from dsmr_backend.tests.mixins import CallCommandStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_stats.models.settings import StatsSettings
from dsmr_weather.models.settings import WeatherSettings
from dsmr_stats.models.statistics import DayStatistics
from dsmr_stats.models.note import Note
import dsmr_consumption.services


class TestViews(CallCommandStdoutMixin, TestCase):
    """ Test whether views render at all. """
    fixtures = [
        'dsmr_frontend/test_dsmrreading.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/EnergySupplierPrice.json',
        'dsmr_frontend/test_statistics.json'
    ]
    namespace = 'frontend'

    def _synchronize_date(self, interval=None):
        """ Little hack to fake any output for today (moment of test). """
        dsmr_consumption.services.compact_all()
        ec = ElectricityConsumption.objects.all()[0]
        gc = GasConsumption.objects.all()[0]
        ds = DayStatistics.objects.get(pk=1)

        timestamp = timezone.now()

        if interval:
            timestamp += interval

        ec.read_at = timestamp
        ec.save()

        gc.read_at = timestamp
        gc.save()

        ds.day = timestamp.date()
        ds.save()

        Note.objects.all().update(day=timestamp.date())
        TemperatureReading.objects.create(read_at=timestamp, degrees_celcius=3.5)

    def setUp(self):
        self.client = Client()

    def test_admin(self):
        response = self.client.get(
            reverse('admin:index')
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], 'http://testserver/admin/login/?next=/admin/'
        )

    def test_dashboard(self):
        weather_settings = WeatherSettings.get_solo()
        weather_settings.track = True
        weather_settings.save()

        self._synchronize_date()
        response = self.client.get(
            reverse('{}:dashboard'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)

        self.assertGreater(
            len(json.loads(response.context['electricity_x'])), 0
        )
        self.assertGreater(
            len(json.loads(response.context['electricity_y'])), 0
        )
        self.assertGreater(len(json.loads(response.context['gas_x'])), 0)
        self.assertGreater(len(json.loads(response.context['gas_y'])), 0)
        self.assertGreater(response.context['latest_electricity'], 0)
        self.assertEqual(response.context['latest_gas'], 0)
        self.assertTrue(response.context['track_temperature'])
        self.assertIn('consumption', response.context)

        # Test whether reverse graphs work.
        frontend_settings = FrontendSettings.get_solo()
        frontend_settings.reverse_dashboard_graphs = True
        frontend_settings.save()

        response = self.client.get(
            reverse('{}:dashboard'.format(self.namespace))
        )

    def test_history(self):
        frontend_settings = FrontendSettings.get_solo()
        frontend_settings.recent_history_weeks = random.randint(1, 5)
        frontend_settings.save()

        # History fetches all data BEFORE today, so add a little interval to make that happen.
        self._synchronize_date(interval=timezone.timedelta(days=-1))
        response = self.client.get(
            reverse('{}:history'.format(self.namespace))
        )
        self.assertTrue(all(x in response.context['usage'][0].keys() for x in [
            'electricity2_returned',
            'electricity1_cost',
            'day',
            'gas',
            'electricity2_cost',
            'electricity2',
            'notes',
            'gas_cost',
            'electricity1',
            'total_cost',
            'average_temperature',
            'electricity1_returned'
        ]))
        self.assertIn('notes', response.context['usage'][0])
        self.assertEqual('Testnote', response.context['usage'][0]['notes'][0])
        self.assertEqual(response.context['days_ago'], frontend_settings.recent_history_weeks * 7)
        self.assertFalse(response.context['track_temperature'])
        self.assertEqual(response.status_code, 200)

    def test_statistics(self):
        self._synchronize_date()
        response = self.client.get(
            reverse('{}:statistics'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)

    def test_trends(self):
        self._synchronize_date()
        trend_url = reverse('{}:trends'.format(self.namespace))

        response = self.client.get(trend_url)
        self.assertEqual(response.status_code, 200)

    def test_status(self):
        self._synchronize_date()
        response = self.client.get(
            reverse('{}:status'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)

        self.assertIn('consumption_settings', response.context)
        self.assertIsInstance(response.context['consumption_settings'], ConsumptionSettings)

        self.assertIn('datalogger_settings', response.context)
        self.assertIsInstance(response.context['datalogger_settings'], DataloggerSettings)

        self.assertIn('frontend_settings', response.context)
        self.assertIsInstance(response.context['frontend_settings'], FrontendSettings)

        self.assertIn('stats_settings', response.context)
        self.assertIsInstance(response.context['stats_settings'], StatsSettings)

        self.assertIn('weather_settings', response.context)
        self.assertIsInstance(response.context['weather_settings'], WeatherSettings)


class TestViewsWithoutData(TestCase):
    namespace = 'frontend'

    def setUp(self):
        self.client = Client()

    def _check_view_status_code(self, view_name):
        response = self.client.get(
            reverse('{}:{}'.format(self.namespace, view_name))
        )
        self.assertEqual(response.status_code, 200)

    def test_dashboard(self):
        """ Check whether dashboard page can run without data. """
        self._check_view_status_code('dashboard')

    def test_history(self):
        """ Check whether history page can run without data. """
        self._check_view_status_code('history')

    def test_statistics(self):
        """ Check whether statistics page can run without data. """
        self._check_view_status_code('statistics')

    def test_trends(self):
        """ Check whether trends page can run without data. """
        self._check_view_status_code('trends')

    def test_status(self):
        """ Check whether status page can run without data. """
        self._check_view_status_code('status')
