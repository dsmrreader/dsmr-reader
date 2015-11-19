from django.test import TestCase, Client
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.management import call_command

from dsmr_stats.models import ElectricityConsumption


class TestViews(TestCase):
    """ Test whether views render at all. """
    fixtures = ['test_dsmrreading.json', 'EnergySupplierPrice.json']
    namespace = 'stats'

    def setUp(self):
        self.client = Client()

    def test_dashboard(self):
        # Little hack to fake any output for today (moment of test).
        call_command('dsmr_stats_compactor')
        ec = ElectricityConsumption.objects.get(pk=1)
        ec.read_at = timezone.now()
        ec.save()

        response = self.client.get(
            reverse('{}:dashboard'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('consumption', response.context)

        consumption = response.context['consumption']
        self.assertGreater(consumption['electricity1_start'], 0)
        self.assertGreater(consumption['electricity2_start'], 0)
        self.assertGreater(consumption['electricity1_end'], 0)
        self.assertGreater(consumption['electricity2_end'], 0)

    def test_history(self):
        response = self.client.get(
            reverse('{}:history'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
