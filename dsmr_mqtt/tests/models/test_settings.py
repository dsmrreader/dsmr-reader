from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_mqtt.models.settings import broker, day_totals, telegram, meter_statistics, consumption, period_totals


class TestSettings(TestCase):
    CLASSES = (
        broker.MQTTBrokerSettings,
        telegram.RawTelegramMQTTSettings,
        telegram.JSONTelegramMQTTSettings,
        telegram.SplitTopicTelegramMQTTSettings,
        day_totals.JSONDayTotalsMQTTSettings,
        day_totals.SplitTopicDayTotalsMQTTSettings,
        meter_statistics.SplitTopicMeterStatisticsMQTTSettings,
        consumption.JSONGasConsumptionMQTTSettings,
        consumption.SplitTopicGasConsumptionMQTTSettings,
        period_totals.JSONCurrentPeriodTotalsMQTTSettings,
        period_totals.SplitTopicCurrentPeriodTotalsMQTTSettings,
    )

    def test_admin(self):
        for current in self.CLASSES:
            self.assertTrue(site.is_registered(current))

    def test_to_string(self):
        for current in self.CLASSES:
            instance = current.get_solo()
            self.assertNotEqual(str(instance), '{} object'.format(instance.__class__.__name__))
