from unittest import mock
from decimal import Decimal

from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.statistics import DayStatistics


class TestViews(TestCase):
    """Test whether views render at all."""

    fixtures = [
        "dsmr_frontend/test_energysupplierprice.json",
        "dsmr_frontend/test_statistics.json",
    ]
    namespace = "frontend"
    support_data = True
    support_gas = True

    def setUp(self):
        self.client = Client()

    @mock.patch("django.utils.timezone.now")
    def test_energy_contracts(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))
        response = self.client.get(
            reverse("{}:energy-contracts".format(self.namespace))
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn("capabilities", response.context)

        self.assertIn("frontend_settings", response.context)
        self.assertIn("energy_contracts", response.context)

        if not EnergySupplierPrice.objects.exists():
            return self.assertEqual(len(response.context["energy_contracts"]), 0)

        self.assertGreater(len(response.context["energy_contracts"]), 0)

        energy_contract = response.context["energy_contracts"][0]
        self.assertIn("start", energy_contract)
        self.assertIn("end", energy_contract)
        self.assertIn("first_day", energy_contract)
        self.assertEqual(energy_contract["description"], "Fake Energy Company")

        if not DayStatistics.objects.exists():
            return

        self.assertEqual(energy_contract["summary"]["electricity1"], Decimal("2.732"))
        self.assertEqual(
            energy_contract["summary"]["electricity1_cost"], Decimal("0.57")
        )
        self.assertEqual(
            energy_contract["summary"]["electricity1_returned"], Decimal("0.000")
        )
        self.assertEqual(energy_contract["summary"]["electricity2"], Decimal("0.549"))
        self.assertEqual(
            energy_contract["summary"]["electricity2_cost"], Decimal("0.12")
        )
        self.assertEqual(
            energy_contract["summary"]["electricity2_returned"], Decimal("0.000")
        )
        self.assertEqual(
            energy_contract["summary"]["electricity_cost_merged"], Decimal("0.69")
        )
        self.assertEqual(
            energy_contract["summary"]["electricity_merged"], Decimal("3.281")
        )
        self.assertEqual(
            energy_contract["summary"]["electricity_returned_merged"], Decimal("0.000")
        )
        self.assertEqual(energy_contract["summary"]["gas"], Decimal("6.116"))
        self.assertEqual(energy_contract["summary"]["gas_cost"], Decimal("3.60"))
        self.assertEqual(energy_contract["summary"]["total_cost"], Decimal("4.29"))


class TestViewsWithoutData(TestViews):
    """Same tests as above, but without any data as it's flushed in setUp()."""

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
    """Same tests as above, but without any price data as it's flushed in setUp()."""

    def setUp(self):
        super(TestViewsWithoutPrices, self).setUp()
        EnergySupplierPrice.objects.all().delete()
        self.assertFalse(EnergySupplierPrice.objects.exists())


class TestViewsWithoutDayStatistics(TestViews):
    fixtures = ["dsmr_frontend/test_energysupplierprice.json"]
    support_data = False

    def setUp(self):
        super(TestViewsWithoutDayStatistics, self).setUp()

        DayStatistics.objects.all().delete()
        self.assertFalse(DayStatistics.objects.exists())


class TestViewsWithoutGas(TestViews):
    """Same tests as above, but without any GAS related data."""

    fixtures = [
        "dsmr_frontend/test_energysupplierprice.json",
        "dsmr_frontend/test_statistics.json",
    ]
    support_gas = False

    def setUp(self):
        super(TestViewsWithoutGas, self).setUp()
        self.assertFalse(GasConsumption.objects.exists())
