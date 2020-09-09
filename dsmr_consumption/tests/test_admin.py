from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls.base import reverse

from dsmr_consumption.models.energysupplier import EnergySupplierPrice


class TestAdmin(TestCase):
    ESP_TEXT = 'Some weird and unique string'
    fixtures = [
        'dsmr_consumption/test_energysupplierprice.json',
    ]
    url = None
    data = None

    def setUp(self):
        username = 'testuser'
        password = 'passwd'
        User.objects.create_superuser(username, 'unknown@localhost', password)

        self.url = reverse('admin:dsmr_consumption_energysupplierprice_add')
        self.data = dict(
            start='2018-01-02',
            end='2020-01-01',
            description=self.ESP_TEXT,
            electricity_delivered_1_price=0,
            electricity_delivered_2_price=0,
            gas_price=0,
            electricity_returned_1_price=0,
            electricity_returned_2_price=0,
            fixed_daily_cost=0,
        )

        self.client = Client()
        self.client.login(username=username, password=password)

    def test_add_esp_okay(self):
        """ Add ESP in new range. """
        self.assertFalse(EnergySupplierPrice.objects.filter(description=self.ESP_TEXT).exists())
        self.client.post(self.url, data=self.data)
        self.assertTrue(EnergySupplierPrice.objects.filter(description=self.ESP_TEXT).exists())

    def test_add_esp_lonely(self):
        """ Add ESP in void. """
        EnergySupplierPrice.objects.all().delete()

        self.data.update(dict(
            fixed_daily_cost=1,
        ))
        self.assertFalse(EnergySupplierPrice.objects.filter(description=self.ESP_TEXT).exists())
        self.client.post(self.url, data=self.data)
        self.assertTrue(EnergySupplierPrice.objects.filter(description=self.ESP_TEXT).exists())

    def test_add_esp_conflict(self):
        """ Add ESP in conflicting range with conflicting price. """
        self.assertFalse(EnergySupplierPrice.objects.filter(description=self.ESP_TEXT).exists())
        self.data.update(dict(
            # Existing contract is between 2015-01-01 and 2018-01-01.
            start='2016-01-01',
            end='2020-01-01',
            # Gas already set by existing contract.
            gas_price=1,
        ))
        self.client.post(self.url, data=self.data)
        self.assertFalse(EnergySupplierPrice.objects.filter(description=self.ESP_TEXT).exists())

    def test_add_esp_merged(self):
        """ Add ESP in conflicting range with different prices that can be merged. """
        self.assertFalse(EnergySupplierPrice.objects.filter(description=self.ESP_TEXT).exists())

        # Unset gas in existing.
        EnergySupplierPrice.objects.all().update(gas_price=0)

        self.data.update(dict(
            # Existing contract is between 2015-01-01 and 2018-01-01.
            start='2016-01-01',
            end='2020-01-01',
            # Gas already set by existing contract.
            gas_price=1,
            # Set but empty
            fixed_daily_cost=0,
        ))
        self.client.post(self.url, data=self.data)
        self.assertTrue(EnergySupplierPrice.objects.filter(description=self.ESP_TEXT).exists())
