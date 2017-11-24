from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_pvoutput.models.settings import PVOutputAPISettings, PVOutputAddStatusSettings
from dsmr_consumption.models.consumption import ElectricityConsumption
import dsmr_pvoutput.services


class TestServices(TestCase):
    fixtures = ['dsmr_pvoutput/electricity-consumption.json']

    def _apply_fake_settings(self):
        api_settings = PVOutputAPISettings.get_solo()
        api_settings.auth_token = 'XXXXX'
        api_settings.system_identifier = 12345
        api_settings.save()

        status_settings = PVOutputAddStatusSettings.get_solo()
        status_settings.export = True
        status_settings.upload_delay = 1
        status_settings.save()

    @mock.patch('django.utils.timezone.now')
    def test_should_export_default(self, now_mock):
        """ Test should_export() default behaviour. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))

        api_settings = PVOutputAPISettings.get_solo()
        status_settings = PVOutputAddStatusSettings.get_solo()

        self.assertIsNone(api_settings.auth_token)
        self.assertFalse(api_settings.system_identifier)
        self.assertFalse(status_settings.export)
        self.assertIsNone(status_settings.next_export)

        self.assertFalse(dsmr_pvoutput.services.should_export())

    @mock.patch('django.utils.timezone.now')
    def test_should_export_no_need(self, now_mock):
        """ Test should_export() when not needed, yet. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))
        self._apply_fake_settings()

        PVOutputAddStatusSettings.objects.update(next_export=timezone.now() + timezone.timedelta(hours=1))
        self.assertFalse(dsmr_pvoutput.services.should_export())

    @mock.patch('django.utils.timezone.now')
    def test_should_export_okay(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))
        self._apply_fake_settings()

        self.assertTrue(dsmr_pvoutput.services.should_export())

    @mock.patch('dsmr_pvoutput.services.should_export')
    @mock.patch('django.utils.timezone.now')
    def test_export_not_allowed(self, now_mock, should_export_mock):
        """ Test export() blocking behaviour. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))
        should_export_mock.return_value = False
        self._apply_fake_settings()

        # Nothing should happen.
        dsmr_pvoutput.services.export()

        self.assertTrue(should_export_mock.called)

        self.assertIsNone(PVOutputAddStatusSettings.get_solo().next_export)

    @mock.patch('requests.post')
    @mock.patch('dsmr_pvoutput.services.should_export')
    @mock.patch('django.utils.timezone.now')
    def test_export_no_electricity(self, now_mock, should_export_mock, requests_mock):
        """ Test export() without electricity. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))
        should_export_mock.return_value = True
        self._apply_fake_settings()

        # Drop all gas data.
        ElectricityConsumption.objects.all().delete()
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(requests_mock.called)

        # Nothing should happen, as there is no data.
        dsmr_pvoutput.services.export()
        self.assertFalse(requests_mock.called)

    @mock.patch('requests.post')
    @mock.patch('dsmr_pvoutput.services.should_export')
    @mock.patch('django.utils.timezone.now')
    def test_export_fail(self, now_mock, should_export_mock, requests_post_mock):
        """ Test export() failing by denied API call. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))
        should_export_mock.return_value = True
        self._apply_fake_settings()

        requests_post_mock.return_value = mock.MagicMock(status_code=400, text='Error message')
        dsmr_pvoutput.services.export()
        settings = PVOutputAddStatusSettings.get_solo()

        self.assertEqual(settings.next_export, timezone.now() + timezone.timedelta(minutes=5))
        self.assertTrue(requests_post_mock.called)

    @mock.patch('requests.post')
    @mock.patch('dsmr_pvoutput.services.should_export')
    @mock.patch('django.utils.timezone.now')
    def test_export_okay(self, now_mock, should_export_mock, requests_post_mock):
        """ Test export() as designed. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))

        should_export_mock.return_value = True
        requests_post_mock.return_value = mock.MagicMock(status_code=200, text='Fake accept')
        self._apply_fake_settings()

        self.assertFalse(requests_post_mock.called)

        dsmr_pvoutput.services.export()

        self.assertIsNotNone(PVOutputAddStatusSettings.get_solo().next_export)
        self.assertTrue(requests_post_mock.called)

        # Check API parameters.
        api_settings = PVOutputAPISettings.get_solo()
        requests_post_mock.assert_called_once_with(
            PVOutputAddStatusSettings.API_URL,
            headers={
                'X-Pvoutput-Apikey': api_settings.auth_token,
                'X-Pvoutput-SystemId': api_settings.system_identifier,
            },
            data={
                'd': '20171001',
                'n': 1,
                't': '13:00',
                'v3': 3000,
                'v4': -750,
            },
        )

        # With processing delay as well.
        requests_post_mock.reset_mock()
        PVOutputAddStatusSettings.objects.update(processing_delay=5, next_export=None)

        dsmr_pvoutput.services.export()

        self.assertIsNotNone(PVOutputAddStatusSettings.get_solo().next_export)
        self.assertTrue(requests_post_mock.called)

        api_settings = PVOutputAPISettings.get_solo()
        requests_post_mock.assert_called_once_with(
            PVOutputAddStatusSettings.API_URL,
            headers={
                'X-Pvoutput-Apikey': api_settings.auth_token,
                'X-Pvoutput-SystemId': api_settings.system_identifier,
            },
            data={
                'd': '20171001',
                'delay': 5,
                'n': 1,
                't': '13:00',
                'v3': 3000,
                'v4': -750,
            },
        )
