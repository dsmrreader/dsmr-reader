from unittest import mock
from decimal import Decimal
import json

from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_stats.models.statistics import DayStatistics


class TestViews(TestCase):
    """Test whether views render at all."""

    fixtures = [
        "dsmr_frontend/test_dsmrreading.json",
        "dsmr_frontend/test_note.json",
        "dsmr_frontend/test_energysupplierprice.json",
        "dsmr_frontend/test_statistics.json",
        "dsmr_frontend/test_meterstatistics.json",
        "dsmr_frontend/test_electricity_consumption.json",
        "dsmr_frontend/test_gas_consumption.json",
    ]
    namespace = "frontend"
    support_data = True
    support_gas = True

    def setUp(self):
        self.client = Client()

    @mock.patch("django.utils.timezone.now")
    def test_statistics(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))
        response = self.client.get(reverse("{}:statistics".format(self.namespace)))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn("capabilities", response.context)
        self.assertIn("electricity_statistics", response.context)

        if DsmrReading.objects.exists():
            self.assertIn("latest_reading", response.context)
            self.assertIn("delivered_sum", response.context)
            self.assertIn("returned_sum", response.context)
            self.assertEqual(response.context["delivered_sum"], Decimal("1059.250"))
            self.assertEqual(response.context["returned_sum"], Decimal("124.356"))

    @mock.patch("django.utils.timezone.now")
    def test_statistics_quarter_hour_maximum_demand(self, now_mock):
        """The maximum demand panels should render when the meter reports the data (Belgium/VREG and similar)."""
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))

        if not self.support_data:
            return

        MeterStatistics.objects.all().update(
            quarter_hour_maximum_demand_running_month=Decimal("1.566"),
            quarter_hour_maximum_demand_running_month_timestamp=timezone.make_aware(
                timezone.datetime(2023, 2, 1, 1, 0, 0)
            ),
            quarter_hour_maximum_demand_last_13_months=[
                {"month": "2023-01-31T23:00:00Z", "peak_timestamp": "2023-01-14T11:45:00Z", "peak_demand": "3.332"}
            ],
        )

        response = self.client.get(reverse("{}:statistics".format(self.namespace)))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, '<span class="badge-integer">1</span><span class="badge-decimal">.566</span>')
        self.assertContains(response, '<span class="badge-integer">3</span><span class="badge-decimal">.332</span>')
        self.assertContains(response, "Wednesday 1 February 2023 at 1:00 a.m.")  # Running month timestamp
        self.assertContains(response, "Wednesday 1 February 2023 at 12:00 a.m.")  # 13 months: month
        self.assertContains(response, "Saturday 14 January 2023 at 12:45 p.m.")  # 13 months: peak timestamp

    def test_statistics_xhr_data(self):
        response = self.client.get(reverse("{}:statistics-xhr-data".format(self.namespace)))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response["Content-Type"], "application/json")

        json_response = json.loads(response.content.decode("utf-8"))
        self.assertIn("total_reading_count", json_response)


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


class TestViewsWithoutGas(TestViews):
    """Same tests as above, but without any GAS related data."""

    fixtures = [
        "dsmr_frontend/test_dsmrreading_without_gas.json",
        "dsmr_frontend/test_note.json",
        "dsmr_frontend/test_energysupplierprice.json",
        "dsmr_frontend/test_statistics.json",
        "dsmr_frontend/test_meterstatistics.json",
        "dsmr_frontend/test_electricity_consumption.json",
    ]
    support_gas = False

    def setUp(self):
        super(TestViewsWithoutGas, self).setUp()
        self.assertFalse(GasConsumption.objects.exists())
