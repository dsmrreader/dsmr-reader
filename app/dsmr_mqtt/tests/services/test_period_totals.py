from decimal import Decimal
from unittest import mock
import json

from django.test import TestCase
from django.utils import timezone

from dsmr_mqtt.models.settings import period_totals
import dsmr_mqtt.services.callbacks


class TestPeriodTotals(TestCase):
    """Shared tests since JSON/split topic use the same data source."""

    fixtures = ["dsmr_mqtt/test_period_totals.json"]

    @mock.patch("django.utils.timezone.now")
    def test_get_period_totals_empty_day_without_day_statistics(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2019, 1, 1))

        result = dsmr_mqtt.services.callbacks.convert_period_totals()
        self.assertEqual(result, {})

    @mock.patch("django.utils.timezone.now")
    def test_get_period_totals_empty_day_with_1_month_statistics(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2021, 1, 1))

        result = dsmr_mqtt.services.callbacks.convert_period_totals()
        self.assertEqual(result["current_month_electricity1"], Decimal("100.000"))
        self.assertEqual(result["current_month_electricity2"], Decimal("200.000"))
        self.assertEqual(
            result["current_month_electricity1_returned"], Decimal("50.000")
        )
        self.assertEqual(
            result["current_month_electricity2_returned"], Decimal("100.000")
        )
        self.assertEqual(result["current_month_electricity_merged"], Decimal("300.000"))
        self.assertEqual(
            result["current_month_electricity_returned_merged"], Decimal("150.000")
        )
        self.assertEqual(result["current_month_electricity1_cost"], Decimal("10.00"))
        self.assertEqual(result["current_month_electricity2_cost"], Decimal("20.00"))
        self.assertEqual(
            result["current_month_electricity_cost_merged"], Decimal("30.00")
        )
        self.assertEqual(result["current_month_gas"], Decimal("300.000"))
        self.assertEqual(result["current_month_gas_cost"], Decimal("30"))
        self.assertEqual(result["current_month_fixed_cost"], Decimal("1.00"))
        self.assertEqual(result["current_month_total_cost"], Decimal("61.00"))

        self.assertEqual(result["current_year_electricity1"], Decimal("200.000"))
        self.assertEqual(result["current_year_electricity2"], Decimal("400.000"))
        self.assertEqual(
            result["current_year_electricity1_returned"], Decimal("100.000")
        )
        self.assertEqual(
            result["current_year_electricity2_returned"], Decimal("200.000")
        )
        self.assertEqual(result["current_year_electricity_merged"], Decimal("600.000"))
        self.assertEqual(
            result["current_year_electricity_returned_merged"], Decimal("300.000")
        )
        self.assertEqual(result["current_year_electricity1_cost"], Decimal("20.00"))
        self.assertEqual(result["current_year_electricity2_cost"], Decimal("40.00"))
        self.assertEqual(
            result["current_year_electricity_cost_merged"], Decimal("60.00")
        )
        self.assertEqual(result["current_year_gas"], Decimal("600.000"))
        self.assertEqual(result["current_year_gas_cost"], Decimal("60"))
        self.assertEqual(result["current_year_fixed_cost"], Decimal("2.00"))
        self.assertEqual(result["current_year_total_cost"], Decimal("122.00"))


class TestJSONPeriodTotals(TestCase):
    fixtures = ["dsmr_mqtt/test_period_totals.json"]

    def setUp(self):
        self.json_settings = (
            period_totals.JSONCurrentPeriodTotalsMQTTSettings.get_solo()
        )

    @mock.patch("dsmr_mqtt.services.messages.queue_message")
    def test_disabled(self, queue_message_mock):
        self.assertFalse(self.json_settings.enabled)
        self.assertFalse(queue_message_mock.called)

        dsmr_mqtt.services.callbacks.publish_json_period_totals()
        self.assertFalse(queue_message_mock.called)

    @mock.patch("dsmr_mqtt.services.messages.queue_message")
    @mock.patch("django.utils.timezone.now")
    def test_no_data(self, now_mock, queue_message_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2019, 1, 1))
        self.json_settings.update(enabled=True)

        self.assertFalse(queue_message_mock.called)
        dsmr_mqtt.services.callbacks.publish_json_period_totals()
        self.assertFalse(queue_message_mock.called)

    @mock.patch("dsmr_mqtt.services.messages.queue_message")
    @mock.patch("django.utils.timezone.now")
    def test_json(self, now_mock, queue_message_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2021, 2, 15, hour=12)
        )
        self.json_settings.update(enabled=True)

        dsmr_mqtt.services.callbacks.publish_json_period_totals()
        self.assertTrue(queue_message_mock.called)

        _, _, result = queue_message_mock.mock_calls[0]
        result = json.loads(result["payload"])

        self.assertEqual(result["current_month_electricity1"], "110.000")
        self.assertEqual(result["current_month_electricity2"], "220.000")
        self.assertEqual(result["current_month_electricity1_returned"], "55.000")
        self.assertEqual(result["current_month_electricity2_returned"], "110.000")
        self.assertEqual(result["current_month_electricity_merged"], "330.000")
        self.assertEqual(result["current_month_electricity_returned_merged"], "165.000")
        self.assertEqual(result["current_month_electricity1_cost"], "15.00")
        self.assertEqual(result["current_month_electricity2_cost"], "40.00")
        self.assertEqual(result["current_month_electricity_cost_merged"], "55.00")
        self.assertEqual(result["current_month_gas"], "301.000")
        self.assertEqual(result["current_month_gas_cost"], "30.50")
        self.assertEqual(result["current_month_fixed_cost"], "2.00")
        self.assertEqual(result["current_month_total_cost"], "87.50")

        self.assertEqual(result["current_year_electricity1"], "210.000")
        self.assertEqual(result["current_year_electricity2"], "420.000")
        self.assertEqual(result["current_year_electricity1_returned"], "105.000")
        self.assertEqual(result["current_year_electricity2_returned"], "210.000")
        self.assertEqual(result["current_year_electricity_merged"], "630.000")
        self.assertEqual(result["current_year_electricity_returned_merged"], "315.000")
        self.assertEqual(result["current_year_electricity1_cost"], "25.00")
        self.assertEqual(result["current_year_electricity2_cost"], "60.00")
        self.assertEqual(result["current_year_electricity_cost_merged"], "85.00")
        self.assertEqual(result["current_year_gas"], "601.000")
        self.assertEqual(result["current_year_gas_cost"], "60.50")
        self.assertEqual(result["current_year_fixed_cost"], "3.00")
        self.assertEqual(result["current_year_total_cost"], "148.50")


class TestSplitTopicPeriodTotals(TestCase):
    fixtures = ["dsmr_mqtt/test_period_totals.json"]

    def setUp(self):
        self.split_topic_settings = (
            period_totals.SplitTopicCurrentPeriodTotalsMQTTSettings.get_solo()
        )

    @mock.patch("dsmr_mqtt.services.messages.queue_message")
    def test_disabled(self, queue_message_mock):
        self.assertFalse(self.split_topic_settings.enabled)
        self.assertFalse(queue_message_mock.called)

        dsmr_mqtt.services.callbacks.publish_split_topic_period_totals()
        self.assertFalse(queue_message_mock.called)

    @mock.patch("dsmr_mqtt.services.messages.queue_message")
    @mock.patch("django.utils.timezone.now")
    def test_no_data(self, now_mock, queue_message_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2019, 1, 1))
        self.split_topic_settings.update(enabled=True)

        self.assertFalse(queue_message_mock.called)
        dsmr_mqtt.services.callbacks.publish_split_topic_period_totals()
        self.assertFalse(queue_message_mock.called)

    @mock.patch("dsmr_mqtt.services.messages.queue_message")
    @mock.patch("django.utils.timezone.now")
    def test_split_topic(self, now_mock, queue_message_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2021, 2, 15, hour=12)
        )
        self.split_topic_settings.update(enabled=True)

        dsmr_mqtt.services.callbacks.publish_split_topic_period_totals()
        self.assertTrue(queue_message_mock.called)

        called_kwargs = [x[1] for x in queue_message_mock.call_args_list]

        expected_data = {
            # Topic: Payload
            "dsmr/current-month/electricity1": Decimal("110.000"),
            "dsmr/current-month/electricity2": Decimal("220.000"),
            "dsmr/current-month/electricity1_returned": Decimal("55.000"),
            "dsmr/current-month/electricity2_returned": Decimal("110.000"),
            "dsmr/current-month/electricity_merged": Decimal("330.000"),
            "dsmr/current-month/electricity_returned_merged": Decimal("165.000"),
            "dsmr/current-month/electricity1_cost": Decimal("15.00"),
            "dsmr/current-month/electricity2_cost": Decimal("40.00"),
            "dsmr/current-month/electricity_cost_merged": Decimal("55.00"),
            "dsmr/current-month/gas": Decimal("301.000"),
            "dsmr/current-month/gas_cost": Decimal("30.50"),
            "dsmr/current-month/fixed_cost": Decimal("2.00"),
            "dsmr/current-month/total_cost": Decimal("87.50"),
            "dsmr/current-year/electricity1": Decimal("210.000"),
            "dsmr/current-year/electricity2": Decimal("420.000"),
            "dsmr/current-year/electricity1_returned": Decimal("105.000"),
            "dsmr/current-year/electricity2_returned": Decimal("210.000"),
            "dsmr/current-year/electricity_merged": Decimal("630.000"),
            "dsmr/current-year/electricity_returned_merged": Decimal("315.000"),
            "dsmr/current-year/electricity1_cost": Decimal("25.00"),
            "dsmr/current-year/electricity2_cost": Decimal("60.00"),
            "dsmr/current-year/electricity_cost_merged": Decimal("85.00"),
            "dsmr/current-year/gas": Decimal("601.000"),
            "dsmr/current-year/gas_cost": Decimal("60.50"),
            "dsmr/current-year/fixed_cost": Decimal("3.00"),
            "dsmr/current-year/total_cost": Decimal("148.50"),
        }

        for expected_topic, expected_payload in expected_data.items():
            self.assertIn(
                {"payload": expected_payload, "topic": expected_topic}, called_kwargs
            )
