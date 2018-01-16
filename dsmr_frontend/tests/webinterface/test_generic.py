from unittest import mock

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.statistics import DayStatistics
import dsmr_consumption.services


class TestViews(TestCase):
    """ Test whether views render at all. """
    fixtures = [
        'dsmr_frontend/test_dsmrreading.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/EnergySupplierPrice.json',
        'dsmr_frontend/test_statistics.json',
        'dsmr_frontend/test_meterstatistics.json',
    ]
    namespace = 'frontend'
    support_data = True
    support_gas = True

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'unknown@localhost', 'passwd')
        dsmr_consumption.services.compact_all()

    def test_admin(self):
        response = self.client.get(
            reverse('admin:index')
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], '/admin/login/?next=/admin/'
        )

    @mock.patch('dsmr_frontend.views.dashboard.Dashboard.get_context_data')
    def test_http_500_production(self, get_context_data_mock):
        get_context_data_mock.side_effect = SyntaxError('Meh')
        response = self.client.get(
            reverse('{}:dashboard'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 500)

    @mock.patch('django.conf.settings.DEBUG')
    @mock.patch('dsmr_frontend.views.dashboard.Dashboard.get_context_data')
    def test_http_500_development(self, get_context_data_mock, debug_setting_mock):
        """ Verify that the middleware is allowing Django to jump in when not in production. """
        get_context_data_mock.side_effect = SyntaxError('Meh')
        debug_setting_mock.return_value = True

        with self.assertRaises(SyntaxError):
            self.client.get(
                reverse('{}:dashboard'.format(self.namespace))
            )

    def test_read_the_docs_redirects(self):
        for current in ('docs', 'feedback'):
            response = self.client.get(reverse('{}:{}-redirect'.format(self.namespace, current)))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response['Location'].startswith('https://dsmr-reader.readthedocs.io'))


class TestViewsWithoutData(TestViews):
    """ Same tests as above, but without any data as it's flushed in setUp().  """
    fixtures = []
    support_data = support_gas = False

    def setUp(self):
        super(TestViewsWithoutData, self).setUp()

        for current_model in (ElectricityConsumption, GasConsumption, DayStatistics):
            current_model.objects.all().delete()

        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())
        self.assertFalse(DayStatistics.objects.exists())


class TestViewsWithoutPrices(TestViews):
    """ Same tests as above, but without any price data as it's flushed in setUp().  """
    def setUp(self):
        super(TestViewsWithoutPrices, self).setUp()
        EnergySupplierPrice.objects.all().delete()
        self.assertFalse(EnergySupplierPrice.objects.exists())


class TestViewsWithoutGas(TestViews):
    """ Same tests as above, but without any GAS related data.  """
    fixtures = [
        'dsmr_frontend/test_dsmrreading_without_gas.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/EnergySupplierPrice.json',
        'dsmr_frontend/test_statistics.json',
        'dsmr_frontend/test_meterstatistics.json',
    ]
    support_gas = False

    def setUp(self):
        super(TestViewsWithoutGas, self).setUp()
        self.assertFalse(GasConsumption.objects.exists())
