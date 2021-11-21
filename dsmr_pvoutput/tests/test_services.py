from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_pvoutput.models.settings import PVOutputAPISettings, PVOutputAddStatusSettings
from dsmr_consumption.models.consumption import ElectricityConsumption
import dsmr_pvoutput.services


class TestServices(TestCase):
    fixtures = ['dsmr_pvoutput/electricity-consumption.json']

    def setUp(self) -> None:
        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_PVOUTPUT_EXPORT)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))

    def _apply_fake_settings(self):
        PVOutputAPISettings.get_solo().update(
            auth_token='XXXXX',
            system_identifier=12345,
        )
        PVOutputAddStatusSettings.get_solo().update(
            export=True,
            upload_delay=1
        )

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
        dsmr_pvoutput.services.get_export_data(
            next_export=timezone.now(), upload_delay=1
        )

        # Make delay again just fall off, failing.
        with self.assertRaises(LookupError):
            dsmr_pvoutput.services.get_export_data(next_export=timezone.now(), upload_delay=2)

    @mock.patch('requests.post')
    def test_export_not_allowed(self, post_mock):
        """ Test export() blocking behaviour. """
        self._apply_fake_settings()
        PVOutputAddStatusSettings.get_solo().update(export=False)
        dsmr_pvoutput.services.run(scheduled_process=self.schedule_process)
        self.assertFalse(post_mock.called)

        self._apply_fake_settings()
        PVOutputAPISettings.get_solo().update(auth_token='')
        dsmr_pvoutput.services.run(scheduled_process=self.schedule_process)
        self.assertFalse(post_mock.called)

        self._apply_fake_settings()
        PVOutputAPISettings.get_solo().update(system_identifier='')
        dsmr_pvoutput.services.run(scheduled_process=self.schedule_process)
        self.assertFalse(post_mock.called)

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_export_no_electricity(self, now_mock, requests_mock):
        """ Test export() without electricity. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))
        self._apply_fake_settings()

        # Drop all electricity data.
        ElectricityConsumption.objects.all().delete()
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(requests_mock.called)

        # Nothing should happen, as there is no data.
        dsmr_pvoutput.services.run(scheduled_process=self.schedule_process)
        self.assertFalse(requests_mock.called)

    @mock.patch('requests.post')
    @mock.patch('dsmr_pvoutput.services.get_export_data')
    @mock.patch('django.utils.timezone.now')
    def test_export_fail(self, now_mock, export_data_mock, requests_post_mock):
        """ Test export() failing by denied API call. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))
        export_data_mock.return_value = {'x': 'y'}  # Unimportant for this test.
        self._apply_fake_settings()

        requests_post_mock.return_value = mock.MagicMock(status_code=400, text='Error message')
        dsmr_pvoutput.services.run(scheduled_process=self.schedule_process)

        # Failure should retry after 5 minutes.
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(minutes=5))
        self.assertTrue(requests_post_mock.called)

    @mock.patch('requests.post')
    @mock.patch('dsmr_pvoutput.services.get_export_data')
    @mock.patch('django.utils.timezone.now')
    @mock.patch('dsmr_pvoutput.signals.pvoutput_upload.send_robust')
    def test_export_postponed(self, send_robust_mock, now_mock, export_data_mock, requests_post_mock):
        """ Test export() but failing due to lack of data ready. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=1))

        export_data_mock.side_effect = LookupError()  # Emulate.
        requests_post_mock.return_value = mock.MagicMock(status_code=200, text='Fake accept')
        self._apply_fake_settings()

        self.assertFalse(requests_post_mock.called)
        self.assertFalse(send_robust_mock.called)

        dsmr_pvoutput.services.run(scheduled_process=self.schedule_process)

        # Nothing should happen.
        self.assertFalse(requests_post_mock.called)
        self.assertFalse(send_robust_mock.called)

    @mock.patch('requests.post')
    @mock.patch('dsmr_pvoutput.services.get_export_data')
    @mock.patch('django.utils.timezone.now')
    @mock.patch('dsmr_pvoutput.signals.pvoutput_upload.send_robust')
    def test_export_okay(self, send_robust_mock, now_mock, export_data_mock, requests_post_mock):
        """ Test export() as designed. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 10, 1, hour=15))
        export_data_mock.return_value = {'x': 'y'}  # Unimportant for this test.

        requests_post_mock.return_value = mock.MagicMock(status_code=200, text='Fake accept')
        self._apply_fake_settings()

        self.assertFalse(requests_post_mock.called)
        self.assertFalse(send_robust_mock.called)

        dsmr_pvoutput.services.run(scheduled_process=self.schedule_process)

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
            timeout=settings.DSMRREADER_CLIENT_TIMEOUT,
        )

        # With processing delay as well.
        requests_post_mock.reset_mock()
        send_robust_mock.reset_mock()
        self.schedule_process.reschedule_asap()
        PVOutputAddStatusSettings.objects.update(processing_delay=5)

        dsmr_pvoutput.services.run(scheduled_process=self.schedule_process)

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
            timeout=settings.DSMRREADER_CLIENT_TIMEOUT,
        )
