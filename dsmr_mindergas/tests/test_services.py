from unittest import mock
import json

from django.test import TestCase
from django.utils import timezone

from dsmr_mindergas.models.settings import MinderGasSettings
from dsmr_consumption.models.consumption import GasConsumption
import dsmr_mindergas.services


class TestServices(TestCase):
    """ Test 'dsmr_backend' management command. """
    fixtures = ['dsmr_mindergas/gas-consumption.json']

    @mock.patch('django.utils.timezone.now')
    def test_should_export_default(self, now_mock):
        """ Test should_export() default behaviour. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=0, minute=5))

        settings = MinderGasSettings.get_solo()
        self.assertFalse(settings.export)
        self.assertIsNone(settings.auth_token)
        self.assertIsNone(settings.next_export)
        self.assertFalse(dsmr_mindergas.services.should_export())

    @mock.patch('django.utils.timezone.now')
    def test_should_export_no_gas(self, now_mock):
        """ Test should_export() without gas. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=0, minute=5))

        settings = MinderGasSettings.get_solo()
        settings.export = True
        settings.auth_token = 'XXXXX'
        settings.save()

        # Drop all gas data.
        GasConsumption.objects.all().delete()
        self.assertFalse(GasConsumption.objects.exists())

        self.assertFalse(dsmr_mindergas.services.should_export())

    @mock.patch('django.utils.timezone.now')
    def test_should_export_no_need(self, now_mock):
        """ Test should_export() when not needed, yet. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=0, minute=5))
        tomorrow = (timezone.localtime(timezone.now()) + timezone.timedelta(hours=24)).date()

        settings = MinderGasSettings.get_solo()
        settings.export = True
        settings.auth_token = 'XXXXX'
        settings.next_export = tomorrow  # Cause of delay.
        settings.save()

        self.assertFalse(dsmr_mindergas.services.should_export())

    @mock.patch('django.utils.timezone.now')
    def test_should_export_okay(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=0, minute=5))

        settings = MinderGasSettings.get_solo()
        settings.export = True
        settings.auth_token = 'XXXXX'
        settings.save()

        self.assertTrue(dsmr_mindergas.services.should_export())

    @mock.patch('dsmr_mindergas.services.should_export')
    @mock.patch('django.utils.timezone.now')
    def test_export_not_allowed(self, now_mock, should_export_mock):
        """ Test export() blocking behaviour. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=0, minute=5))
        should_export_mock.return_value = False

        settings = MinderGasSettings.get_solo()
        self.assertFalse(settings.export)
        self.assertIsNone(settings.next_export)
        self.assertFalse(should_export_mock.called)

        # Nothing should happen.
        dsmr_mindergas.services.export()

        self.assertTrue(should_export_mock.called)
        self.assertIsNone(settings.next_export)

    @mock.patch('dsmr_mindergas.services.should_export')
    @mock.patch('django.utils.timezone.now')
    def test_export_no_gas(self, now_mock, should_export_mock):
        """ Test export() without gas data. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=0, minute=5))
        should_export_mock.return_value = True

        # Drop all gas data.
        GasConsumption.objects.all().delete()
        self.assertFalse(GasConsumption.objects.exists())

        settings = MinderGasSettings.get_solo()
        self.assertFalse(settings.export)
        self.assertIsNone(settings.next_export)

        # Nothing should happen, as there is no data.
        dsmr_mindergas.services.export()
        self.assertIsNone(settings.next_export)

    @mock.patch('requests.post')
    @mock.patch('dsmr_mindergas.services.should_export')
    @mock.patch('django.utils.timezone.now')
    def test_export_fail(self, now_mock, should_export_mock, requests_post_mock):
        """ Test export() failing by denied API call. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=0, minute=5))
        should_export_mock.return_value = True

        settings = MinderGasSettings.get_solo()
        self.assertFalse(settings.export)
        self.assertIsNone(settings.next_export)
        self.assertFalse(requests_post_mock.called)

        # Mindergas error codes according to docs.
        for current_error_code in (401, 422):
            requests_post_mock.return_value = mock.MagicMock(status_code=current_error_code, text='Error message')

            with self.assertRaises(AssertionError):
                dsmr_mindergas.services.export()

        settings = MinderGasSettings.get_solo()
        self.assertIsNone(settings.next_export)
        self.assertTrue(requests_post_mock.called)

    @mock.patch('requests.post')
    @mock.patch('dsmr_mindergas.services.should_export')
    @mock.patch('django.utils.timezone.now')
    def test_export_okay(self, now_mock, should_export_mock, requests_post_mock):
        """ Test export() as designed. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=0, minute=5))
        should_export_mock.return_value = True
        requests_post_mock.return_value = mock.MagicMock(status_code=201, text='Fake accept')

        settings = MinderGasSettings.get_solo()
        self.assertFalse(settings.export)
        self.assertIsNone(settings.next_export)
        self.assertFalse(requests_post_mock.called)

        dsmr_mindergas.services.export()
        settings = MinderGasSettings.get_solo()
        self.assertIsNotNone(settings.next_export)
        self.assertTrue(requests_post_mock.called)

        # Check API parameters.
        requests_post_mock.assert_called_once_with(
            MinderGasSettings.API_URL,
            headers={'Content-Type': 'application/json', 'AUTH-TOKEN': settings.auth_token},
            data=json.dumps({'date': '2015-12-11', 'reading': '956.739'}),
        )
