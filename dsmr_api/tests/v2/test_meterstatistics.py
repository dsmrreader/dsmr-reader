from unittest import mock

from django.utils import timezone

from dsmr_api.tests.v2 import APIv2TestCase
from dsmr_datalogger.models.statistics import MeterStatistics


class TestMeterStatistics(APIv2TestCase):
    fixtures = ['dsmr_api/test_dsmrreading.json']

    @mock.patch('django.utils.timezone.now')
    def test_get(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 1, 1))

        MeterStatistics.get_solo()
        MeterStatistics.objects.all().update(
            timestamp=timezone.now(),
            dsmr_version='50',
            electricity_tariff=1,
            power_failure_count=123,
            long_power_failure_count=456,
            voltage_sag_count_l1=11,
            voltage_sag_count_l2=22,
            voltage_sag_count_l3=33,
            voltage_swell_count_l1=44,
            voltage_swell_count_l2=55,
            voltage_swell_count_l3=66,
        )

        result = self._request('meter-statistics')

        self.assertEqual(result['id'], 1)
        self.assertEqual(result['timestamp'], '2020-01-01T00:00:00+01:00')
        self.assertEqual(result['dsmr_version'], '50')
        self.assertEqual(result['electricity_tariff'], 1)
        self.assertEqual(result['latest_telegram'], None)
        self.assertEqual(result['power_failure_count'], 123)
        self.assertEqual(result['long_power_failure_count'], 456)
        self.assertEqual(result['voltage_sag_count_l1'], 11)
        self.assertEqual(result['voltage_sag_count_l2'], 22)
        self.assertEqual(result['voltage_sag_count_l3'], 33)
        self.assertEqual(result['voltage_swell_count_l1'], 44)
        self.assertEqual(result['voltage_swell_count_l2'], 55)
        self.assertEqual(result['voltage_swell_count_l3'], 66)

    @mock.patch('django.utils.timezone.now')
    def test_patch(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 1, 1))

        instance = MeterStatistics.get_solo()
        EXPECTED = dict(
            dsmr_version=None,
            electricity_tariff=None,
            power_failure_count=None,
            long_power_failure_count=None,
            voltage_sag_count_l1=None,
            voltage_sag_count_l2=None,
            voltage_sag_count_l3=None,
            voltage_swell_count_l1=None,
            voltage_swell_count_l2=None,
            voltage_swell_count_l3=None,
        )

        # Check default (empty) state in database.
        [
            self.assertEqual(
                getattr(instance, k),
                expected_value,
                k
            )
            for k, expected_value in EXPECTED.items()
        ]

        # Partial update.
        self._request('meter-statistics', expected_code=200, method='patch', data=dict(
            timestamp='2020-01-15T12:34:56+01:00',
            dsmr_version='50',
            electricity_tariff=1,
            power_failure_count=123,
            long_power_failure_count=456,
        ))

        EXPECTED = dict(
            dsmr_version='50',
            electricity_tariff=1,
            power_failure_count=123,
            long_power_failure_count=456,
            voltage_sag_count_l1=None,
            voltage_sag_count_l2=None,
            voltage_sag_count_l3=None,
            voltage_swell_count_l1=None,
            voltage_swell_count_l2=None,
            voltage_swell_count_l3=None,
        )

        # Check partial updated state in database.
        instance.refresh_from_db()
        [
            self.assertEqual(
                getattr(instance, k),
                expected_value,
                k
            )
            for k, expected_value in EXPECTED.items()
        ]
        self.assertEqual(str(instance.timestamp), '2020-01-15 11:34:56+00:00')  # Shifted to UTC

        self._request('meter-statistics', expected_code=200, method='patch', data=dict(
            dsmr_version='42',
            electricity_tariff=2,
            power_failure_count=77777,
            long_power_failure_count=8888,
            voltage_sag_count_l1=11,
            voltage_sag_count_l2=22,
            voltage_sag_count_l3=33,
            voltage_swell_count_l1=44,
            voltage_swell_count_l2=55,
            voltage_swell_count_l3=66,
        ))

        EXPECTED = dict(
            dsmr_version='42',
            electricity_tariff=2,
            power_failure_count=77777,
            long_power_failure_count=8888,
            voltage_sag_count_l1=11,
            voltage_sag_count_l2=22,
            voltage_sag_count_l3=33,
            voltage_swell_count_l1=44,
            voltage_swell_count_l2=55,
            voltage_swell_count_l3=66,
        )

        # Check final updated state in database.
        instance.refresh_from_db()
        [
            self.assertEqual(
                getattr(instance, k),
                expected_value,
                k
            )
            for k, expected_value in EXPECTED.items()
        ]
