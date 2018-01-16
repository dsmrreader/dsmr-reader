from unittest import mock
import json

from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.statistics import DayStatistics
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
    def test_status(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))
        response = self.client.get(
            reverse('{}:status'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)

        self.assertIn('capabilities', response.context)
        self.assertIn('unprocessed_readings', response.context)
        self.assertIn('unprocessed_reading_span', response.context)

        if self.support_data:
            self.assertIn('latest_day_statistics', response.context)
            self.assertIn('days_since_latest_day_statistics', response.context)
            self.assertIsNone(response.context['unprocessed_reading_span'])

            # Check unprocessed count as well.
            DsmrReading.objects.update(processed=False)
            response = self.client.get(
                reverse('{}:status'.format(self.namespace))
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['unprocessed_readings'], 3)
            self.assertEqual(response.context['unprocessed_reading_span'], 11953)

        if 'latest_reading' in response.context:
            self.assertIn('delta_since_latest_reading', response.context)

        if 'latest_ec' in response.context:
            self.assertIn('latest_ec', response.context)
            self.assertIn('minutes_since_latest_ec', response.context)

        if 'latest_gc' in response.context:
            self.assertIn('latest_gc', response.context)
            self.assertIn('hours_since_latest_gc', response.context)

    @mock.patch('django.utils.timezone.now')
    def test_status_back_to_the_future(self, now_mock):
        """ Test some weird situation having the smart meter reporting a future timestamp in the telegrams. """
        if not self.support_data:
            self.skipTest('No data')

        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 2, 1))

        latest_reading = DsmrReading.objects.all().order_by('-timestamp')[0]
        DsmrReading.objects.exclude(pk=latest_reading.pk).delete()
        latest_reading.timestamp = timezone.now() + timezone.timedelta(seconds=15)  # Future reading.
        latest_reading.save()

        response = self.client.get(
            reverse('{}:status'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)

        # These should be reset for convenience.
        self.assertEqual(response.context['latest_reading'].timestamp, timezone.now())
        self.assertEqual(response.context['delta_since_latest_reading'], 0)

    @mock.patch('dsmr_backend.services.is_latest_version')
    def test_status_xhr_update_checker(self, is_latest_version_mock):
        for boolean in (True, False):
            is_latest_version_mock.return_value = boolean

            response = self.client.get(
                reverse('{}:status-xhr-check-for-updates'.format(self.namespace))
            )
            self.assertEqual(response.status_code, 200, response.content)
            self.assertEqual(response['Content-Type'], 'application/json')

            json_response = json.loads(response.content.decode("utf-8"))
            self.assertIn('update_available', json_response)
            self.assertEqual(json_response['update_available'], not boolean)  # Inverted, because latest = no updates.


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
