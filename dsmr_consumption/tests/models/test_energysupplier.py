from django.utils import timezone
from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_consumption.models.energysupplier import EnergySupplierPrice


class TestEnergySupplierPrice(TestCase):
    def setUp(self):
        self.instance = EnergySupplierPrice.objects.create(
            start=timezone.now(),
            end=timezone.now(),
            description='Test',
            electricity_delivered_1_price=1,
            electricity_delivered_2_price=2,
            gas_price=3,
            electricity_returned_1_price=1,
            electricity_returned_2_price=2,
        )

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(EnergySupplierPrice))

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'EnergySupplierPrice')
