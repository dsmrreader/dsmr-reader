from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_consumption.models.energysupplier import EnergySupplierPrice


class TestEnergySupplierPrice(TestCase):
    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(EnergySupplierPrice))
