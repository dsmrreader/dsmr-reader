from unittest import mock
import json

from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import F

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_weather.models.settings import WeatherSettings
from dsmr_stats.models.statistics import DayStatistics
from dsmr_frontend.models.message import Notification
from dsmr_datalogger.models.reading import DsmrReading
import dsmr_consumption.services
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_weather.models.reading import TemperatureReading


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

    @mock.patch('django.utils.timezone.now')
    def test_dashboard(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 11, 15))

        weather_settings = WeatherSettings.get_solo()
        weather_settings.track = True
        weather_settings.save()

        response = self.client.get(
            reverse('{}:dashboard'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('frontend_settings', response.context)
        self.assertEqual(
            response.context['frontend_settings'].dashboard_graph_width,
            FrontendSettings.get_solo().dashboard_graph_width
        )

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
                reverse('{}:dashboard-xhr-header'.format(self.namespace))
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
                        json_response['cost_per_hour'], '0.23' if current_tariff == 1 else '0.46'
                    )

    def test_dashboard_xhr_header_future(self):
        # Set timestamp to the future, so the view will reset the timestamp displayed to 'now'.
        DsmrReading.objects.all().update(timestamp=F('timestamp') + timezone.timedelta(weeks=999))

        response = self.client.get(
            reverse('{}:dashboard-xhr-header'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_dashboard_xhr_consumption(self):
        response = self.client.get(
            reverse('{}:dashboard-xhr-consumption'.format(self.namespace))
        )

        self.assertEqual(response.status_code, 200, response.content)

        if self.support_data:
            self.assertIn('consumption', response.context)

    @mock.patch('django.utils.timezone.now')
    def test_dashboard_xhr_electricity(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 7, 1))

        if self.support_data:
            ElectricityConsumption.objects.create(
                read_at=timezone.now(),
                delivered_1=0,
                returned_1=0,
                delivered_2=0,
                returned_2=0,
                currently_delivered=1.5,
                currently_returned=0.1,
                phase_currently_delivered_l1=0.5,
                phase_currently_delivered_l2=0.25,
                phase_currently_delivered_l3=0.75,
            )
            ElectricityConsumption.objects.create(
                read_at=timezone.now() - timezone.timedelta(hours=1),
                delivered_1=0,
                returned_1=0,
                delivered_2=0,
                returned_2=0,
                currently_delivered=2.5,
                currently_returned=0.2,
                phase_currently_delivered_l1=0.75,
                phase_currently_delivered_l2=0.5,
                phase_currently_delivered_l3=1.25,
            )

        response = self.client.get(
            reverse('{}:dashboard-xhr-electricity'.format(self.namespace)),
            data={'delivered': True, 'returned': True, 'phases': True}
        )

        if not self.support_data:
            return self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(response.status_code, 200, response.content)

        json_content = json.loads(response.content.decode("utf8"))
        self.assertGreater(json_content['latest_delta_id'], 0)
        self.assertEqual(
            json_content,
            {
                'latest_delta_id': json_content['latest_delta_id'],  # Not hardcoded due to DB backend differences.
                'read_at': ['Sat 23:00', 'Sun 0:00'],
                'currently_delivered': [2500.0, 1500.0],
                'currently_returned': [200.0, 100.0],
                'phases': {
                    'l1': [750.0, 500.0],
                    'l2': [500.0, 250.0],
                    'l3': [1250.0, 750.0],
                }
            }
        )

        # Branch tests for each option.
        response = self.client.get(
            reverse('{}:dashboard-xhr-electricity'.format(self.namespace)),
            data={'delivered': True, 'returned': True, 'phases': False}
        )
        self.assertEqual(response.status_code, 200, response.content)

        json_content = json.loads(response.content.decode("utf8"))
        self.assertNotEqual(json_content['read_at'], [])
        self.assertNotEqual(json_content['currently_delivered'], [])
        self.assertNotEqual(json_content['currently_returned'], [])
        self.assertEqual(json_content['phases']['l1'], [])
        self.assertEqual(json_content['phases']['l2'], [])
        self.assertEqual(json_content['phases']['l3'], [])

        response = self.client.get(
            reverse('{}:dashboard-xhr-electricity'.format(self.namespace)),
            data={'delivered': False, 'returned': False, 'phases': False}
        )
        json_content = json.loads(response.content.decode("utf8"))
        self.assertNotEqual(json_content['read_at'], [])
        self.assertEqual(json_content['currently_delivered'], [])
        self.assertEqual(json_content['currently_returned'], [])
        self.assertEqual(json_content['phases']['l1'], [])
        self.assertEqual(json_content['phases']['l2'], [])
        self.assertEqual(json_content['phases']['l3'], [])

        # Send again, but with small delta update.
        old_latest_delta_id = json_content['latest_delta_id']
        response = self.client.get(
            reverse('{}:dashboard-xhr-electricity'.format(self.namespace)),
            data={'delivered': True, 'returned': True, 'phases': True, 'latest_delta_id': old_latest_delta_id}
        )
        self.assertEqual(response.status_code, 200, response.content)

        # The delta sorting of this test is completely wrong, because the consumptions are created backwards above.
        json_content = json.loads(response.content.decode("utf8"))
        self.assertGreater(json_content['latest_delta_id'], old_latest_delta_id)
        self.assertEqual(
            json_content,
            {
                'latest_delta_id': json_content['latest_delta_id'],  # Not hardcoded due to DB backend differences.
                'read_at': ['Sat 23:00'],
                'currently_delivered': [2500.0],
                'currently_returned': [200.0],
                'phases': {
                    'l1': [750.0],
                    'l2': [500.0],
                    'l3': [1250.0],
                }
            }
        )

    @mock.patch('django.utils.timezone.now')
    def test_dashboard_xhr_gas(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 7, 1))

        if self.support_data:
            DataloggerSettings.objects.update(track_phases=True)
            GasConsumption.objects.create(
                read_at=timezone.now(),
                delivered=0,
                currently_delivered=1,
            )

            GasConsumption.objects.create(
                read_at=timezone.now() - timezone.timedelta(hours=1),
                delivered=0,
                currently_delivered=0.5,
            )

        response = self.client.get(
            reverse('{}:dashboard-xhr-gas'.format(self.namespace))
        )
        json_content = json.loads(response.content.decode("utf8"))

        if self.support_data:
            self.assertEqual(json_content, {'currently_delivered': [0.5, 1.0], 'read_at': ['Sat 23:00', 'Sun 0:00']})
        else:
            self.assertEqual(json_content, {'read_at': [], 'currently_delivered': []})

    @mock.patch('django.utils.timezone.now')
    def test_dashboard_xhr_temperature(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 7, 1))

        if self.support_data:
            weather_settings = WeatherSettings.get_solo()
            weather_settings.track = True
            weather_settings.save()

            TemperatureReading.objects.create(
                read_at=timezone.now(),
                degrees_celcius=20,
            )

            TemperatureReading.objects.create(
                read_at=timezone.now() - timezone.timedelta(hours=1),
                degrees_celcius=30,
            )

        response = self.client.get(
            reverse('{}:dashboard-xhr-temperature'.format(self.namespace))
        )
        json_content = json.loads(response.content.decode("utf8"))

        if self.support_data:
            self.assertEqual(json_content, {'degrees_celcius': [30.0, 20.0], 'read_at': ['Sat 23:00', 'Sun 0:00']})
        else:
            self.assertEqual(json_content, {'read_at': [], 'degrees_celcius': []})

    def test_dashboard_xhr_notification_read(self):
        view_url = reverse('{}:dashboard-xhr-notification-read'.format(self.namespace))
        notification = Notification.objects.create(message='TEST', redirect_to='fake')
        self.assertFalse(notification.read)

        response = self.client.post(view_url, data={'notification_id': notification.pk})
        self.assertEqual(response.status_code, 200)

        # Notification should be altered now.
        notification.refresh_from_db()
        self.assertTrue(notification.read)


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
