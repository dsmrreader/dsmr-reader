from unittest import mock

from django.test import TestCase

from dsmr_mqtt.models.settings import meter_statistics
from dsmr_datalogger.models.statistics import MeterStatistics
import dsmr_mqtt.services.callbacks


class TestDaytotals(TestCase):
    def setUp(self):
        self.split_topic_settings = meter_statistics.SplitTopicMeterStatisticsMQTTSettings.get_solo()

        # Mapping.
        self.split_topic_settings.formatting = '''
[mapping]
# DATA = JSON FIELD
dsmr_version = dsmr/aaa
electricity_tariff = dsmr/bbb
power_failure_count = dsmr/ccc
long_power_failure_count = dsmr/ddd
voltage_sag_count_l1 = dsmr/eee
voltage_sag_count_l2 = dsmr/fff
voltage_sag_count_l3 = dsmr/ggg
voltage_swell_count_l1 = dsmr/hhh
voltage_swell_count_l2 = dsmr/iii
voltage_swell_count_l3 = dsmr/jjj
rejected_telegrams = dsmr/kkk
'''
        self.split_topic_settings.save()

    @mock.patch('dsmr_mqtt.models.queue.Message.objects.create')
    def test_disabled(self, create_message_mock):
        self.assertFalse(self.split_topic_settings.enabled)
        self.assertFalse(create_message_mock.called)

        dsmr_mqtt.services.callbacks.publish_split_topic_meter_statistics()
        self.assertFalse(create_message_mock.called)

    @mock.patch('dsmr_mqtt.models.queue.Message.objects.create')
    def test_split_topic(self, create_message_mock):
        MeterStatistics.objects.all().update(**{
            "timestamp": "2018-03-13T19:52:14Z",
            "dsmr_version": "42",
            "electricity_tariff": 2,
            "power_failure_count": 5,
            "long_power_failure_count": 2,
            "voltage_sag_count_l1": 2,
            "voltage_sag_count_l2": 2,
            "voltage_sag_count_l3": 0,
            "voltage_swell_count_l1": 0,
            "voltage_swell_count_l2": 0,
            "voltage_swell_count_l3": 0,
            "rejected_telegrams": 96
        })

        # Should be okay now.
        self.split_topic_settings.enabled = True
        self.split_topic_settings.save()
        dsmr_mqtt.services.callbacks.publish_split_topic_meter_statistics()
        self.assertTrue(create_message_mock.called)

        called_kwargs = [x[1] for x in create_message_mock.call_args_list]

        # Without gas or costs.
        self.assertIn({'payload': '42', 'topic': 'dsmr/aaa'}, called_kwargs)
        self.assertIn({'payload': 2, 'topic': 'dsmr/bbb'}, called_kwargs)
        self.assertIn({'payload': 5, 'topic': 'dsmr/ccc'}, called_kwargs)
        self.assertIn({'payload': 2, 'topic': 'dsmr/ddd'}, called_kwargs)
        self.assertIn({'payload': 2, 'topic': 'dsmr/eee'}, called_kwargs)
        self.assertIn({'payload': 2, 'topic': 'dsmr/fff'}, called_kwargs)
        self.assertIn({'payload': 0, 'topic': 'dsmr/ggg'}, called_kwargs)
        self.assertIn({'payload': 0, 'topic': 'dsmr/hhh'}, called_kwargs)
        self.assertIn({'payload': 0, 'topic': 'dsmr/iii'}, called_kwargs)
        self.assertIn({'payload': 0, 'topic': 'dsmr/jjj'}, called_kwargs)
        self.assertIn({'payload': 96, 'topic': 'dsmr/kkk'}, called_kwargs)
