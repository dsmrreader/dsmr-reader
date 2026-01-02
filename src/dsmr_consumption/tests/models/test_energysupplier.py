from decimal import Decimal

from django.utils import timezone
from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_consumption.models.energysupplier import EnergySupplierPrice


class TestEnergySupplierPrice(TestCase):
    def setUp(self):
        self.instance = EnergySupplierPrice.objects.create(
            start=timezone.now(),
            end=timezone.now(),
            description="Test",
            electricity_delivered_1_price=Decimal("0.123456"),
            electricity_delivered_2_price=Decimal("1.234567"),
            gas_price=Decimal("2.345678"),
            electricity_returned_1_price=Decimal("3.456789"),
            electricity_returned_2_price=Decimal("4.567890"),
            fixed_daily_cost=Decimal("5.678901"),
        )

        # WARNING: Ensure that DB is actually used here, for decimal constraints validation below!
        self.instance = EnergySupplierPrice.objects.all()[0]

    def test_admin(self):
        """Model should be registered in Django Admin."""
        self.assertTrue(site.is_registered(EnergySupplierPrice))

    def test_decimals(self):
        """Max decimals."""
        self.assertEqual(str(self.instance.electricity_delivered_1_price), "0.123456")
        self.assertEqual(str(self.instance.electricity_delivered_2_price), "1.234567")
        self.assertEqual(str(self.instance.gas_price), "2.345678")
        self.assertEqual(str(self.instance.electricity_returned_1_price), "3.456789")
        self.assertEqual(str(self.instance.electricity_returned_2_price), "4.567890")
        self.assertEqual(str(self.instance.fixed_daily_cost), "5.678901")

    def test_str(self):
        """Model should override string formatting."""
        self.assertNotEqual(str(self.instance), "EnergySupplierPrice")
