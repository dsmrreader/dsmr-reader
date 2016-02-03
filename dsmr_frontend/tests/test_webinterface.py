import json

from django.test import TestCase, Client
from django.utils import timezone
from django.core.urlresolvers import reverse

from dsmr_backend.tests.mixins import CallCommandStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_stats.models.note import Note
from dsmr_weather.models.statistics import TemperatureReading


class TestViews(CallCommandStdoutMixin, TestCase):
    """ Test whether views render at all. """
    fixtures = [
        'dsmr_frontend/test_dsmrreading.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/EnergySupplierPrice.json'
    ]
    namespace = 'frontend'

    def _synchronize_date(self, interval=None):
        """ Little hack to fake any output for today (moment of test). """
        self._call_command_stdout('dsmr_backend')
        ec = ElectricityConsumption.objects.get(pk=1)
        gc = GasConsumption.objects.get(pk=1)

        timestamp = timezone.now()

        if interval:
            timestamp += interval

        ec.read_at = timestamp
        gc.read_at = timestamp
        ec.save()
        gc.save()

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
        self.assertFalse(response.context['track_temperature'])
        self.assertIn('consumption', response.context)

    def test_history(self):
        # History fetches all data BEFORE today, so add a little interval to make that happen.
        self._synchronize_date(interval=timezone.timedelta(hours=-24))
        response = self.client.get(
            reverse('{}:history'.format(self.namespace))
        )
        self.assertIn('usage', response.context)
        self.assertIn('notes', response.context['usage'][0])
        self.assertEqual(response.context['usage'][0]['notes'][0], 'Gourmetten')
        self.assertFalse(response.context['track_temperature'])

        self.assertEqual(response.status_code, 200)

    def test_statistics(self):
        self._synchronize_date()
        response = self.client.get(
            reverse('{}:statistics'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
