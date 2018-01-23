from unittest import mock
from datetime import date

from django.test import TestCase, Client
from django.utils import timezone, formats
from django.urls import reverse
from django.contrib.auth.models import User

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_stats.models.statistics import DayStatistics
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
    def test_archive(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))
        response = self.client.get(
            reverse('{}:archive'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('capabilities', response.context)

        # XHR's.
        data = {
            'date': formats.date_format(timezone.now().date(), 'DSMR_DATEPICKER_DATE_FORMAT'),
        }

        if self.support_data:
            self.assertEqual(response.context['start_date'], date(2016, 1, 1))
            self.assertEqual(response.context['end_date'], date(2016, 1, 2))

        for current_level in ('days', 'months', 'years'):
            # Test both with tariffs sparated and merged.
            for merge in (False, True):
                frontend_settings = FrontendSettings.get_solo()
                frontend_settings.merge_electricity_tariffs = merge
                frontend_settings.save()

                data.update({'level': current_level})
                response = self.client.get(
                    reverse('{}:archive-xhr-summary'.format(self.namespace)), data=data
                )
                self.assertEqual(response.status_code, 200)

                response = self.client.get(
                    reverse('{}:archive-xhr-graphs'.format(self.namespace)), data=data
                )
                self.assertEqual(response.status_code, 200, response.content)

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
