from unittest import mock
import json

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_mindergas.models.settings import MinderGasSettings
from dsmr_consumption.models.consumption import GasConsumption
import dsmr_mindergas.services


class TestServices(TestCase):
    fixtures = ['dsmr_mindergas/gas-consumption.json']
    schedule_process = None
    mindergas_settings = None

    def setUp(self):
        self.mindergas_settings = MinderGasSettings.get_solo()
        self.mindergas_settings.update(export=True, auth_token='12345')

        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_MINDERGAS_EXPORT)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2017, 1, 1)))

    def test_no_auth_token(self):
        """ Having no auth token should disable settings. """
        self.mindergas_settings.update(auth_token=None)

        dsmr_mindergas.services.run(self.schedule_process)

        self.mindergas_settings.refresh_from_db()
        self.schedule_process.refresh_from_db()
        self.assertFalse(self.mindergas_settings.export)
        self.assertFalse(self.schedule_process.active)

    @mock.patch('dsmr_backend.services.backend.get_capabilities')
    @mock.patch('django.utils.timezone.now')
    def test_no_gas(self, now_mock, capa_mock):
        """ Having no gas should postpone. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 1, 1))
        capa_mock.return_value = False

        dsmr_mindergas.services.run(self.schedule_process)

        self.schedule_process.refresh_from_db()
        self.assertTrue(self.schedule_process.active)
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=1))

    @mock.patch('dsmr_backend.services.backend.get_capabilities')
    @mock.patch('dsmr_mindergas.services.export')
    @mock.patch('django.utils.timezone.now')
    def test_call_export_okay(self, now_mock, export_mock, capa_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 1, 1))
        capa_mock.return_value = True

        dsmr_mindergas.services.run(self.schedule_process)

        self.assertTrue(export_mock.called)
        self.schedule_process.refresh_from_db()
        self.assertGreater(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=24))
        self.assertLess(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=25))

    @mock.patch('dsmr_frontend.services.display_dashboard_message')
    @mock.patch('dsmr_backend.services.backend.get_capabilities')
    @mock.patch('dsmr_mindergas.services.export')
    @mock.patch('django.utils.timezone.now')
    def test_call_export_error(self, now_mock, export_mock, capa_mock, message_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 1, 1))
        capa_mock.return_value = True
        export_mock.side_effect = IOError('Random error')

        dsmr_mindergas.services.run(self.schedule_process)

        self.assertTrue(message_mock.called)
        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=1))

    @mock.patch('django.utils.timezone.now')
    def test_export_no_gas(self, now_mock):
        """ Test without gas data. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=0, minute=5))

        # Drop all gas data.
        GasConsumption.objects.all().delete()
        self.assertFalse(GasConsumption.objects.exists())

        with self.assertRaises(AssertionError):
            dsmr_mindergas.services.export()

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_export_fail(self, now_mock, requests_post_mock):
        """ Test failing by denied API call. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=4, minute=45))

        # Mindergas error codes according to docs.
        for current_error_code in (401, 422):
            requests_post_mock.return_value = mock.MagicMock(status_code=current_error_code, text='Error message')

            with self.assertRaises(AssertionError):
                dsmr_mindergas.services.export()

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_export_okay(self, now_mock, requests_post_mock):
        """ Test as designed. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=0, minute=5))
        requests_post_mock.return_value = mock.MagicMock(status_code=201, text='Fake OK')

        dsmr_mindergas.services.export()

        # Check API parameters.
        requests_post_mock.assert_called_once_with(
            MinderGasSettings.API_URL,
            headers={
                'Content-Type': 'application/json',
                'AUTH-TOKEN': self.mindergas_settings.auth_token,
                'User-Agent': settings.DSMRREADER_USER_AGENT
            },
            data=json.dumps({'date': '2015-12-11', 'reading': '956.739'}),
        )
