import json

from django.test import TestCase, Client
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.management import call_command

from dsmr_stats.models import ElectricityConsumption, GasConsumption


class TestViews(TestCase):
    """ Test whether views render at all. """
    fixtures = ['test_dsmrreading.json', 'EnergySupplierPrice.json']
    namespace = 'stats'

    def _synchronize_date(self):
        # Little hack to fake any output for today (moment of test).
        call_command('dsmr_stats_compactor')
        ec = ElectricityConsumption.objects.get(pk=1)
        gc = GasConsumption.objects.get(pk=1)
        ec.read_at = timezone.now()
        gc.read_at = timezone.now()
        ec.save()
        gc.save()

    def setUp(self):
        self.client = Client()

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

    def test_history(self):
        response = self.client.get(
            reverse('{}:history'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)

    def test_statistics(self):
        self._synchronize_date()
        response = self.client.get(
            reverse('{}:statistics'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)

    def test_energy_supplier_prices(self):
        response = self.client.get(
            reverse('{}:energy-supplier-prices'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
