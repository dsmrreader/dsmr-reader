from unittest import mock

from django.conf import settings
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
    def test_get_next_export(self, now_mock):
        PVOutputAddStatusSettings.get_solo()

        PVOutputAddStatusSettings.objects.update(upload_interval=PVOutputAddStatusSettings.INTERVAL_5_MINUTES)
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 2, 1, hour=12, minute=13, second=15))
        result = dsmr_pvoutput.services.get_next_export()

        self.assertEqual(result.hour, 12)
        self.assertEqual(result.minute, 15)
        self.assertEqual(result.second, 0)

        PVOutputAddStatusSettings.objects.update(upload_interval=PVOutputAddStatusSettings.INTERVAL_15_MINUTES)
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 2, 1, hour=12, minute=25, second=50))
        result = dsmr_pvoutput.services.get_next_export()
        self.assertEqual(result.hour, 12)
        self.assertEqual(result.minute, 30)
        self.assertEqual(result.second, 0)

        # Pass hour mark.
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 2, 1, hour=12, minute=59, second=30))
        result = dsmr_pvoutput.services.get_next_export()
        self.assertEqual(result.hour, 13)
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.second, 0)

    @mock.patch('django.utils.timezone.now')
    def test_get_export_data(self, now_mock):
        """ Complexity to make sure the upload is in sync. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 9, 30, hour=15))
        self._apply_fake_settings()

        # Too soon, no data in today's range.
        result = dsmr_pvoutput.services.get_export_data(next_export=timezone.now(), upload_delay=0)
        self.assertIsNone(result)

        # First sync, next day.
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=13))  # Include 2 EC's.
        result = dsmr_pvoutput.services.get_export_data(next_export=None, upload_delay=0)
        self.assertEqual(result, {'d': '20171001', 'n': 1, 't': '13:00', 'v3': 4000, 'v4': -750})

        # Now with all test EC's.
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))  # Include all 3 EC's.
        result = dsmr_pvoutput.services.get_export_data(next_export=None, upload_delay=0)
        self.assertEqual(result, {'d': '20171001', 'n': 1, 't': '15:00', 'v3': 7000, 'v4': 450})

        # Now with delay, should not be allowed, as we wait for more data.
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=13))  # Include 2 EC's.
        with self.assertRaises(LookupError):
            dsmr_pvoutput.services.get_export_data(next_export=timezone.now(), upload_delay=1)

        # Again with delay, but we move forward in time.
        now_mock.return_value = now_mock.return_value + timezone.timedelta(minutes=1)
        result = dsmr_pvoutput.services.get_export_data(
            next_export=timezone.now(), upload_delay=1
        )

        # Make delay again just fall off, failing.
        with self.assertRaises(LookupError):
            dsmr_pvoutput.services.get_export_data(next_export=timezone.now(), upload_delay=2)

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
    @mock.patch('dsmr_pvoutput.services.get_export_data')
    @mock.patch('django.utils.timezone.now')
    def test_export_fail(self, now_mock, export_data_mock, should_export_mock, requests_post_mock):
        """ Test export() failing by denied API call. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))
        export_data_mock.return_value = {'x': 'y'}  # Unimportant for this test.
        should_export_mock.return_value = True
        self._apply_fake_settings()

        requests_post_mock.return_value = mock.MagicMock(status_code=400, text='Error message')
        dsmr_pvoutput.services.export()

        status_settings = PVOutputAddStatusSettings.get_solo()
        self.assertEqual(status_settings.next_export, timezone.now() + timezone.timedelta(minutes=5))
        self.assertTrue(requests_post_mock.called)
        self.assertIsNone(status_settings.latest_sync)

    @mock.patch('requests.post')
    @mock.patch('dsmr_pvoutput.services.should_export')
    @mock.patch('dsmr_pvoutput.services.get_export_data')
    @mock.patch('django.utils.timezone.now')
    @mock.patch('dsmr_pvoutput.signals.pvoutput_upload.send_robust')
    def test_export_postponed(
        self, send_robust_mock, now_mock, export_data_mock, should_export_mock, requests_post_mock
    ):
        """ Test export() but failing due to lack of data ready. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=1))

        should_export_mock.return_value = True
        export_data_mock.side_effect = LookupError()  # Emulate.
        requests_post_mock.return_value = mock.MagicMock(status_code=200, text='Fake accept')
        self._apply_fake_settings()

        self.assertFalse(requests_post_mock.called)
        self.assertFalse(send_robust_mock.called)

        dsmr_pvoutput.services.export()

        # Nothing should happen.
        self.assertFalse(requests_post_mock.called)
        self.assertFalse(send_robust_mock.called)

    @mock.patch('requests.post')
    @mock.patch('dsmr_pvoutput.services.should_export')
    @mock.patch('dsmr_pvoutput.services.get_export_data')
    @mock.patch('django.utils.timezone.now')
    @mock.patch('dsmr_pvoutput.signals.pvoutput_upload.send_robust')
    def test_export_okay(self, send_robust_mock, now_mock, export_data_mock, should_export_mock, requests_post_mock):
        """ Test export() as designed. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))
        export_data_mock.return_value = {'x': 'y'}  # Unimportant for this test.

        should_export_mock.return_value = True
        requests_post_mock.return_value = mock.MagicMock(status_code=200, text='Fake accept')
        self._apply_fake_settings()

        self.assertFalse(requests_post_mock.called)
        self.assertFalse(send_robust_mock.called)

        dsmr_pvoutput.services.export()

        self.assertIsNotNone(PVOutputAddStatusSettings.get_solo().next_export)
        self.assertTrue(requests_post_mock.called)
        self.assertTrue(send_robust_mock.called)

        # Check API parameters.
        api_settings = PVOutputAPISettings.get_solo()
        requests_post_mock.assert_called_once_with(
            PVOutputAddStatusSettings.API_URL,
            headers={
                'User-Agent': settings.DSMRREADER_USER_AGENT,
                'X-Pvoutput-Apikey': api_settings.auth_token,
                'X-Pvoutput-SystemId': api_settings.system_identifier,
            },
            data={'x': 'y'},
        )

        # With processing delay as well.
        requests_post_mock.reset_mock()
        send_robust_mock.reset_mock()
        PVOutputAddStatusSettings.objects.update(processing_delay=5, next_export=None)

        dsmr_pvoutput.services.export()

        status_settings = PVOutputAddStatusSettings.get_solo()
        self.assertIsNotNone(status_settings.next_export)
        self.assertEqual(status_settings.latest_sync, timezone.now())
        self.assertTrue(requests_post_mock.called)
        self.assertTrue(send_robust_mock.called)

        api_settings = PVOutputAPISettings.get_solo()
        requests_post_mock.assert_called_once_with(
            PVOutputAddStatusSettings.API_URL,
            headers={
                'User-Agent': settings.DSMRREADER_USER_AGENT,
                'X-Pvoutput-Apikey': api_settings.auth_token,
                'X-Pvoutput-SystemId': api_settings.system_identifier,
            },
            data={
                'x': 'y',
                'delay': 5,
            },
        )
