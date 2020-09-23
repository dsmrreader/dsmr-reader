from unittest import mock
import json

from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_weather.models.settings import WeatherSettings
from dsmr_stats.models.statistics import DayStatistics
from dsmr_weather.models.reading import TemperatureReading


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

    def setUp(self):
        self.client = Client()

    @mock.patch('django.utils.timezone.now')
    def test_live_graphs(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 11, 15))

        weather_settings = WeatherSettings.get_solo()
        weather_settings.track = True
        weather_settings.save()

        response = self.client.get(
            reverse('{}:live-graphs'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn('frontend_settings', response.context)

    @mock.patch('django.utils.timezone.now')
    def test_live_xhr_electricity(self, now_mock):
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
                phase_currently_returned_l1=2.5,
                phase_currently_returned_l2=2.25,
                phase_currently_returned_l3=2.75,
                phase_voltage_l1=230,
                phase_power_current_l1=1,
                phase_power_current_l2=2,
                phase_power_current_l3=3
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
                phase_currently_returned_l1=3.5,
                phase_currently_returned_l2=3.25,
                phase_currently_returned_l3=3.75,
                phase_voltage_l1=230,
                phase_power_current_l1=11,
                phase_power_current_l2=22,
                phase_power_current_l3=33
            )

        response = self.client.get(
            reverse('{}:live-xhr-electricity'.format(self.namespace)),
            dict(delivered=True, returned=True, phases=True, power_current=True)
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
                'phases_delivered': {
                    'l1': [750.0, 500.0],
                    'l2': [500.0, 250.0],
                    'l3': [1250.0, 750.0],
                },
                'phases_returned': {
                    'l1': [3500.0, 2500.0],
                    'l2': [3250.0, 2250.0],
                    'l3': [3750.0, 2750.0],
                },
                'phase_voltage': {'l1': [], 'l2': [], 'l3': []},
                'phase_power_current': {'l1': [11, 1], 'l2': [22, 2], 'l3': [33, 3]},
            }
        )

        # Branch tests for each option.
        response = self.client.get(
            reverse('{}:live-xhr-electricity'.format(self.namespace)),
            dict(delivered=True, returned=True, phases=False, power_current=False)
        )
        self.assertEqual(response.status_code, 200, response.content)

        json_content = json.loads(response.content.decode("utf8"))
        self.assertNotEqual(json_content['read_at'], [])
        self.assertNotEqual(json_content['currently_delivered'], [])
        self.assertNotEqual(json_content['currently_returned'], [])
        self.assertEqual(json_content['phases_delivered']['l1'], [])
        self.assertEqual(json_content['phases_delivered']['l2'], [])
        self.assertEqual(json_content['phases_delivered']['l3'], [])
        self.assertEqual(json_content['phases_returned']['l1'], [])
        self.assertEqual(json_content['phases_returned']['l2'], [])
        self.assertEqual(json_content['phases_returned']['l3'], [])

        response = self.client.get(
            reverse('{}:live-xhr-electricity'.format(self.namespace)),
            dict(delivered=True, returned=False, phases=True, power_current=False)
        )
        self.assertEqual(response.status_code, 200, response.content)

        json_content = json.loads(response.content.decode("utf8"))
        self.assertNotEqual(json_content['read_at'], [])
        self.assertNotEqual(json_content['currently_delivered'], [])
        self.assertEqual(json_content['currently_returned'], [])
        self.assertNotEqual(json_content['phases_delivered']['l1'], [])
        self.assertNotEqual(json_content['phases_delivered']['l2'], [])
        self.assertNotEqual(json_content['phases_delivered']['l3'], [])
        self.assertEqual(json_content['phases_returned']['l1'], [])
        self.assertEqual(json_content['phases_returned']['l2'], [])
        self.assertEqual(json_content['phases_returned']['l3'], [])

        response = self.client.get(
            reverse('{}:live-xhr-electricity'.format(self.namespace)),
            dict(delivered=False, returned=False, phases=False, power_current=False)
        )
        json_content = json.loads(response.content.decode("utf8"))
        self.assertNotEqual(json_content['read_at'], [])
        self.assertEqual(json_content['currently_delivered'], [])
        self.assertEqual(json_content['currently_returned'], [])
        self.assertEqual(json_content['phases_delivered']['l1'], [])
        self.assertEqual(json_content['phases_delivered']['l2'], [])
        self.assertEqual(json_content['phases_delivered']['l3'], [])
        self.assertEqual(json_content['phases_returned']['l1'], [])
        self.assertEqual(json_content['phases_returned']['l2'], [])
        self.assertEqual(json_content['phases_returned']['l3'], [])

        # Send again, but with small delta update.
        old_latest_delta_id = json_content['latest_delta_id']
        response = self.client.get(
            reverse('{}:live-xhr-electricity'.format(self.namespace)),
            data=dict(
                delivered=True,
                returned=True,
                phases=True,
                power_current=True,
                latest_delta_id=old_latest_delta_id
            )
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
                'phases_delivered': {
                    'l1': [750.0],
                    'l2': [500.0],
                    'l3': [1250.0],
                },
                'phases_returned': {
                    'l1': [3500.0],
                    'l2': [3250.0],
                    'l3': [3750.0],
                },
                'phase_voltage': {'l1': [], 'l2': [], 'l3': []},
                'phase_power_current': {'l1': [11], 'l2': [22], 'l3': [33]},
            }
        )

        # Voltages
        response = self.client.get(
            reverse('{}:live-xhr-electricity'.format(self.namespace)),
            dict(voltage=True, latest_delta_id=old_latest_delta_id)
        )
        self.assertEqual(response.status_code, 200, response.content)
        json_content = json.loads(response.content.decode("utf8"))
        self.assertEqual(
            json_content,
            {
                'latest_delta_id': json_content['latest_delta_id'],  # Not hardcoded due to DB backend differences.
                'read_at': ['Sat 23:00'],
                'currently_delivered': [],
                'currently_returned': [],
                'phases_delivered': {
                    'l1': [],
                    'l2': [],
                    'l3': [],
                },
                'phases_returned': {
                    'l1': [],
                    'l2': [],
                    'l3': [],
                },
                'phase_voltage': {'l1': [230], 'l2': [0.0], 'l3': [0.0]},
                'phase_power_current': {'l1': [], 'l2': [], 'l3': []},
            }
        )

        # Power current
        response = self.client.get(
            reverse('{}:live-xhr-electricity'.format(self.namespace)),
            dict(power_current=True, latest_delta_id=old_latest_delta_id)
        )
        self.assertEqual(response.status_code, 200, response.content)
        json_content = json.loads(response.content.decode("utf8"))
        self.assertEqual(
            json_content,
            {
                'latest_delta_id': json_content['latest_delta_id'],  # Not hardcoded due to DB backend differences.
                'read_at': ['Sat 23:00'],
                'currently_delivered': [],
                'currently_returned': [],
                'phases_delivered': {
                    'l1': [],
                    'l2': [],
                    'l3': [],
                },
                'phases_returned': {
                    'l1': [],
                    'l2': [],
                    'l3': [],
                },
                'phase_voltage': {'l1': [], 'l2': [], 'l3': []},
                'phase_power_current': {'l1': [11], 'l2': [22], 'l3': [33]},
            }
        )

        # Fix for bug #506.
        ElectricityConsumption.objects.update(phase_currently_delivered_l1=None)
        response = self.client.get(
            reverse('{}:live-xhr-electricity'.format(self.namespace)),
            dict(delivered=True, returned=True, phases=True)
        )
        self.assertEqual(response.status_code, 200, response.content)

    @mock.patch('django.utils.timezone.now')
    def test_live_xhr_gas(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 7, 1))

        if self.support_data:
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
            reverse('{}:live-xhr-gas'.format(self.namespace))
        )
        json_content = json.loads(response.content.decode("utf8"))

        if self.support_data:
            self.assertEqual(json_content, {'currently_delivered': [0.5, 1.0], 'read_at': ['Sat 23:00', 'Sun 0:00']})
        else:
            self.assertEqual(json_content, {'read_at': [], 'currently_delivered': []})

    @mock.patch('django.utils.timezone.now')
    def test_live_xhr_temperature(self, now_mock):
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
            reverse('{}:live-xhr-temperature'.format(self.namespace))
        )
        json_content = json.loads(response.content.decode("utf8"))

        if self.support_data:
            self.assertEqual(json_content, {'degrees_celcius': [30.0, 20.0], 'read_at': ['Sat 23:00', 'Sun 0:00']})
        else:
            self.assertEqual(json_content, {'read_at': [], 'degrees_celcius': []})


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
        'dsmr_frontend/test_energysupplierprice.json',
        'dsmr_frontend/test_statistics.json',
        'dsmr_frontend/test_meterstatistics.json',
        'dsmr_frontend/test_electricity_consumption.json',
    ]
    support_gas = False

    def setUp(self):
        super(TestViewsWithoutGas, self).setUp()
        self.assertFalse(GasConsumption.objects.exists())
