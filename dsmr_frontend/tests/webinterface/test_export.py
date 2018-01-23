import io

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.statistics import DayStatistics
from dsmr_frontend.forms import ExportAsCsvForm
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

    def test_export(self):
        view_url = reverse('{}:export'.format(self.namespace))
        # Check login required.
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], '/admin/login/?next={}'.format(view_url)
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
            response['Location'], '/admin/login/?next={}'.format(view_url)
        )

        # Login and retest, without post data.
        self.client.login(username='testuser', password='passwd')
        response = self.client.post(view_url,)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            # Invalid form redirects to previous page.
            response['Location'], '{}'.format(
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
