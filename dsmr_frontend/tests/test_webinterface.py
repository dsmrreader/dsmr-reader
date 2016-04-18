from unittest import mock
import json
import io

from django.test import TestCase, Client
from django.utils import timezone, formats
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_weather.models.settings import WeatherSettings
from dsmr_stats.models.statistics import DayStatistics
from dsmr_datalogger.models.reading import DsmrReading
import dsmr_consumption.services
from dsmr_frontend.forms import ExportAsCsvForm


class TestViews(TestCase):
    """ Test whether views render at all. """
    fixtures = [
        'dsmr_frontend/test_dsmrreading.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/EnergySupplierPrice.json',
        'dsmr_frontend/test_statistics.json'
    ]
    namespace = 'frontend'
    support_data = True
    support_gas = True

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'unknown@localhost', 'passwd')
        dsmr_consumption.services.compact_all()

    def test_admin(self):
        response = self.client.get(
            reverse('admin:index')
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], 'http://testserver/admin/login/?next=/admin/'
        )

    @mock.patch('dsmr_frontend.views.dashboard.Dashboard.get_context_data')
    def test_http_500_production(self, get_context_data_mock):
        get_context_data_mock.side_effect = SyntaxError('Meh')
        response = self.client.get(
            reverse('{}:dashboard'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 500)

    @mock.patch('django.conf.settings.DEBUG')
    @mock.patch('dsmr_frontend.views.dashboard.Dashboard.get_context_data')
    def test_http_500_development(self, get_context_data_mock, debug_setting_mock):
        """ Verify that the middleware is allowing Django to jump in when not in production. """
        get_context_data_mock.side_effect = SyntaxError('Meh')
        debug_setting_mock.return_value = True

        with self.assertRaises(SyntaxError):
            self.client.get(
                reverse('{}:dashboard'.format(self.namespace))
            )

    @mock.patch('django.utils.timezone.now')
    def test_dashboard(self, now_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 1, 1)
        )

        weather_settings = WeatherSettings.get_solo()
        weather_settings.track = True
        weather_settings.save()

        response = self.client.get(
            reverse('{}:dashboard'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)

        if self.support_data:
            self.assertGreater(
                len(json.loads(response.context['electricity_x'])), 0
            )
            self.assertGreater(
                len(json.loads(response.context['electricity_y'])), 0
            )

            self.assertGreater(response.context['latest_electricity'], 0)
            self.assertTrue(response.context['track_temperature'])
            self.assertIn('consumption', response.context)

        if self.support_gas:
            self.assertGreater(len(json.loads(response.context['gas_x'])), 0)
            self.assertGreater(len(json.loads(response.context['gas_y'])), 0)
            self.assertEqual(response.context['latest_gas'], 0)

        # Test whether reverse graphs work.
        frontend_settings = FrontendSettings.get_solo()
        frontend_settings.reverse_dashboard_graphs = True
        frontend_settings.save()

        response = self.client.get(
            reverse('{}:dashboard'.format(self.namespace))
        )

    @mock.patch('django.utils.timezone.now')
    def test_archive(self, now_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 1, 1)
        )
        response = self.client.get(
            reverse('{}:archive'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('capabilities', response.context)

        # XHR's.
        data = {
            'date': formats.date_format(timezone.now().date(), 'DSMR_DATEPICKER_DATE_FORMAT'),
        }
        for current_level in ('days', 'months', 'years'):
            data.update({'level': current_level})
            response = self.client.get(
                reverse('{}:archive-xhr-summary'.format(self.namespace)), data=data
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn('capabilities', response.context)

            response = self.client.get(
                reverse('{}:archive-xhr-graphs'.format(self.namespace)), data=data
            )
            self.assertEqual(response.status_code, 200)

        # Invalid XHR.
        data.update({'level': 'INVALID DATA'})
        response = self.client.get(
            reverse('{}:archive-xhr-summary'.format(self.namespace)), data=data
        )
        self.assertEqual(response.status_code, 500)
        response = self.client.get(
            reverse('{}:archive-xhr-graphs'.format(self.namespace)), data=data
        )
        self.assertEqual(response.status_code, 500)

    @mock.patch('django.utils.timezone.now')
    def test_statistics(self, now_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 1, 1)
        )
        response = self.client.get(
            reverse('{}:statistics'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('capabilities', response.context)

        if DsmrReading.objects.exists():
            self.assertIn('latest_reading', response.context)

    @mock.patch('django.utils.timezone.now')
    def test_trends(self, now_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 1, 1)
        )
        response = self.client.get(
            reverse('{}:trends'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('capabilities', response.context)
        self.assertIn('day_statistics_count', response.context)
        self.assertIn('hour_statistics_count', response.context)

        if 'avg_consumption_x' in response.context:
            self.assertIn('electricity_by_tariff_week', response.context)
            self.assertIn('electricity_by_tariff_month', response.context)

        # Test with missing electricity returned.
        ElectricityConsumption.objects.all().update(currently_returned=0)
        response = self.client.get(
            reverse('{}:trends'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['capabilities']['electricity_returned'])

    @mock.patch('django.utils.timezone.now')
    def test_compare(self, now_mock):
        """ Basicly the same view (context vars) as the archive view. """
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 1, 1)
        )
        response = self.client.get(
            reverse('{}:compare'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('capabilities', response.context)

    @mock.patch('django.utils.timezone.now')
    def test_status(self, now_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 1, 1)
        )
        response = self.client.get(
            reverse('{}:status'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)

        self.assertIn('capabilities', response.context)
        self.assertIn('total_reading_count', response.context)
        self.assertIn('unprocessed_readings', response.context)

        if 'latest_reading' in response.context:
            self.assertIn('first_reading', response.context)
            self.assertIn('delta_since_latest_reading', response.context)

        if 'latest_ec' in response.context:
            self.assertIn('delta_since_latest_ec', response.context)

        if 'latest_gc' in response.context:
            self.assertIn('delta_since_latest_gc', response.context)

    def test_export(self):
        view_url = reverse('{}:export'.format(self.namespace))
        # Check login required.
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], 'http://testserver/admin/login/?next={}'.format(view_url)
        )

        # Login and retest
        self.client.login(username='testuser', password='passwd')
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('start_date', response.context)
        self.assertIn('end_date', response.context)

    def test_export_as_csv(self):
        view_url = reverse('{}:export-as-csv'.format(self.namespace))
        post_data = {
            'data_type': ExportAsCsvForm.DATA_TYPE_DAY,
            'export_format': ExportAsCsvForm.EXPORT_FORMAT_CSV,
            'start_date': '2016-01-01',
            'end_date': '2016-02-01',
        }

        # Check login required.
        response = self.client.post(view_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], 'http://testserver/export/admin/login/?next={}'.format(view_url)
        )

        # Login and retest, without post data.
        self.client.login(username='testuser', password='passwd')
        response = self.client.post(view_url,)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            # Invalid form redirects to previous page.
            response['Location'], 'http://testserver{}'.format(
                reverse('{}:export'.format(self.namespace))
            )
        )

        # Day export.
        response = self.client.post(view_url, data=post_data)
        self.assertEqual(response.status_code, 200)
        io.BytesIO(b"".join(response.streaming_content))  # Force generator evaluation.

        # Hour export.
        post_data['data_type'] = ExportAsCsvForm.DATA_TYPE_HOUR
        response = self.client.post(view_url, data=post_data)
        self.assertEqual(response.status_code, 200)
        io.BytesIO(b"".join(response.streaming_content))  # Force generator evaluation.

    @mock.patch('django.utils.timezone.now')
    def test_configuration(self, now_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 1, 1)
        )

        # Check login required.
        response = self.client.get(
            reverse('{}:configuration'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 302)

        # Login and retest
        self.client.login(username='testuser', password='passwd')
        response = self.client.get(
            reverse('{}:configuration'.format(self.namespace))
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('consumption_settings', response.context)
        self.assertIsInstance(response.context['consumption_settings'], ConsumptionSettings)

        self.assertIn('datalogger_settings', response.context)
        self.assertIsInstance(response.context['datalogger_settings'], DataloggerSettings)

        self.assertIn('frontend_settings', response.context)
        self.assertIsInstance(response.context['frontend_settings'], FrontendSettings)

        self.assertIn('weather_settings', response.context)
        self.assertIsInstance(response.context['weather_settings'], WeatherSettings)


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


class TestViewsWithoutGas(TestViews):
    """ Same tests as above, but without any GAS related data.  """
    fixtures = [
        'dsmr_frontend/test_dsmrreading_without_gas.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/EnergySupplierPrice.json',
        'dsmr_frontend/test_statistics.json'
    ]
    support_gas = False

    def setUp(self):
        super(TestViewsWithoutGas, self).setUp()
        self.assertFalse(GasConsumption.objects.exists())
