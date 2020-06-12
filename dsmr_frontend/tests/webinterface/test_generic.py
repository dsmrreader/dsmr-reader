import json
from decimal import Decimal
from unittest import mock

from django.test.utils import override_settings
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_stats.models.statistics import DayStatistics


class TestViews(TestCase):
    """ Test whether views render at all. """
    fixtures = [
        'dsmr_frontend/test_dsmrreading.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/test_energysupplierprice.json',
        'dsmr_frontend/test_statistics.json',
        'dsmr_frontend/test_meterstatistics.json',
        'dsmr_frontend/test_electricity_consumption.json',
        'dsmr_frontend/test_gas_consumption.json',
    ]
    namespace = 'frontend'
    support_data = True
    support_gas = True
    support_prices = True

    def setUp(self):
        self.client = Client()

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

    @override_settings(DEBUG=True)
    @mock.patch('dsmr_frontend.views.dashboard.Dashboard.get_context_data')
    def test_http_500_development(self, get_context_data_mock):
        """ Verify that the middleware is allowing Django to jump in when not in production. """
        get_context_data_mock.side_effect = SyntaxError('Meh')

        with self.assertRaises(SyntaxError):
            self.client.get(
                reverse('{}:dashboard'.format(self.namespace))
            )

    def test_read_the_docs_redirects(self):
        for current in ('docs', 'feedback'):
            response = self.client.get(reverse('{}:{}-redirect'.format(self.namespace, current)))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response['Location'].startswith('https://dsmr-reader.readthedocs.io'))

    @mock.patch('django.utils.timezone.now')
    def test_dashboard_xhr_header(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 11, 15))

        # This makes sure all possible code paths are covered.
        for current_tariff in (None, 1, 2):
            if MeterStatistics.objects.exists():
                meter_statistics = MeterStatistics.get_solo()
                meter_statistics.electricity_tariff = current_tariff
                meter_statistics.save()

            response = self.client.get(
                reverse('{}:xhr-consumption-header'.format(self.namespace))
            )
            self.assertEqual(response.status_code, 200, response.content)
            self.assertEqual(response['Content-Type'], 'application/json')

            # No response when no data at all.
            if self.support_data:
                json_response = json.loads(response.content.decode("utf-8"))
                self.assertIn('timestamp', json_response)
                self.assertIn('currently_delivered', json_response)
                self.assertIn('currently_returned', json_response)

                # Costs only makes sense when set.
                if EnergySupplierPrice.objects.exists() and MeterStatistics.objects.exists() \
                        and current_tariff is not None:
                    self.assertIn('cost_per_hour', json_response)
                    self.assertEqual(
                        json_response['cost_per_hour'], '0.23' if current_tariff == 1 else '0.45'
                    )

    def test_dashboard_xhr_header_future(self):
        """ Test whether future timestamps are reset to now. """
        # Set timestamp to the future, so the view will reset the timestamp displayed to 'now'.
        DsmrReading.objects.all().update(
            timestamp=timezone.now() + timezone.timedelta(weeks=1),
        )

        response = self.client.get(
            reverse('{}:xhr-consumption-header'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response['Content-Type'], 'application/json')

        if not self.support_data:
            return

        json_response = json.loads(response.content)
        self.assertEqual(json_response['timestamp'], 'now')

    @mock.patch('django.utils.timezone.now')
    def test_dashboard_xhr_header_electricity_return_negate_costs(self, now_mock):
        """ Test whether electricity return negate the costs. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 11, 15))

        if self.support_data:
            latest = DsmrReading.objects.all().order_by('-timestamp')[0]
            # Test data is unrealistic, but changing it hits other tests, so we'll just reset it here.
            latest.update(
                electricity_currently_delivered=Decimal(0),
                electricity_currently_returned=Decimal(1.234),
            )

        response = self.client.get(
            reverse('{}:xhr-consumption-header'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response['Content-Type'], 'application/json')

        if not self.support_data or not self.support_prices:
            return

        json_response = json.loads(response.content)
        self.assertEqual(json_response['cost_per_hour'], '-0.12')


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
        self.support_prices = False


class TestViewsWithoutGas(TestViews):
    """ Same tests as above, but without any GAS related data.  """
    fixtures = [
        'dsmr_frontend/test_dsmrreading_without_gas.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/test_energysupplierprice.json',
        'dsmr_frontend/test_statistics.json',
        'dsmr_frontend/test_meterstatistics.json',
        'dsmr_frontend/test_electricity_consumption.json',
    ]
    support_gas = False

    def setUp(self):
        super(TestViewsWithoutGas, self).setUp()
        self.assertFalse(GasConsumption.objects.exists())
