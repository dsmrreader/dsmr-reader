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
        self.assertIn('track_temperature', response.context)

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
                    self.assertIn('latest_electricity_cost', json_response)
                    self.assertEqual(
                        json_response['latest_electricity_cost'], '0.23' if current_tariff == 1 else '0.46'
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
    def test_dashboard_xhr_graphs(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 11, 15))

        if self.support_data:
            weather_settings = WeatherSettings.get_solo()
            weather_settings.track = True
            weather_settings.save()

            # Test with phases feature switched on as well.
            DataloggerSettings.get_solo()
            DataloggerSettings.objects.update(track_phases=True)

        # Send seperate offset as well.
        response = self.client.get(
            reverse('{}:dashboard-xhr-graphs'.format(self.namespace)),
            data={'electricity_offset': 24, 'gas_offset': 10}
        )
        self.assertEqual(response.status_code, 200, response.content)

        # Send invalid offset.
        response = self.client.get(
            reverse('{}:dashboard-xhr-graphs'.format(self.namespace)),
            data={'electricity_offset': 'abc', 'gas_offset': 'xzy'}
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            reverse('{}:dashboard-xhr-graphs'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200, response.content)
        json_content = json.loads(response.content.decode("utf8"))

        if self.support_data:
            self.assertGreater(
                len(json_content['electricity_x']), 0
            )
            self.assertGreater(
                len(json_content['electricity_y']), 0
            )

            self.assertIn('phases_l1_y', json_content)
            self.assertIn('phases_l2_y', json_content)
            self.assertIn('phases_l3_y', json_content)

        if self.support_gas:
            self.assertGreater(len(json_content['gas_x']), 0)
            self.assertGreater(len(json_content['gas_y']), 0)

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
