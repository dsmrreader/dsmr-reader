from unittest import mock
import json

from django.test import TestCase
from django.utils import timezone

from dsmr_consumption.models.consumption import GasConsumption
from dsmr_mqtt.models.settings import consumption
import dsmr_mqtt.services.callbacks


class TestServices(TestCase):
    def _create_gas_consumption(self):
        return GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=1500,
            currently_delivered=0.75,
        )


class TestTelegramAndReading(TestServices):
    @mock.patch('dsmr_mqtt.services.callbacks.publish_json_gas_consumption')
    @mock.patch('dsmr_mqtt.services.callbacks.publish_split_topic_gas_consumption')
    def test_create_signal(self, *service_mocks):
        self.assertFalse(all([x.called for x in service_mocks]))
        self._create_gas_consumption()
        self.assertTrue(all([x.called for x in service_mocks]))

        # Check exception handling.
        for x in service_mocks:
            x.reset_mock()
            x.side_effect = EnvironmentError('Random error')

        self.assertFalse(all([x.called for x in service_mocks]))
        gas_consumption = self._create_gas_consumption()
        self.assertTrue(all([x.called for x in service_mocks]))

        # Check signal for only new models.
        for x in service_mocks:
            x.reset_mock()

        self.assertFalse(all([x.called for x in service_mocks]))
        gas_consumption.currently_delivered = 1
        gas_consumption.save()
        self.assertFalse(all([x.called for x in service_mocks]))

    @mock.patch('dsmr_mqtt.services.messages.queue_message')
    @mock.patch('django.utils.timezone.now')
    def test_publish_json_gas_consumption(self, now_mock, queue_message_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2020, 1, 1), timezone=timezone.utc
        )
        json_settings = consumption.JSONGasConsumptionMQTTSettings.get_solo()
        gas_consumption = self._create_gas_consumption()

        # Mapping.
        json_settings.formatting = '''
[mapping]
read_at = aaa
delivered = bbb
currently_delivered = ccc
'''
        json_settings.save()

        # Disabled by default.
        self.assertFalse(json_settings.enabled)
        self.assertFalse(queue_message_mock.called)
        dsmr_mqtt.services.callbacks.publish_json_gas_consumption(instance=gas_consumption)
        self.assertFalse(queue_message_mock.called)

        # Now enabled.
        json_settings.enabled = True
        json_settings.save()
        dsmr_mqtt.services.callbacks.publish_json_gas_consumption(instance=gas_consumption)
        self.assertTrue(queue_message_mock.called)

        _, _, kwargs = queue_message_mock.mock_calls[0]
        payload = json.loads(kwargs['payload'])

        self.assertEqual(payload['aaa'], '2020-01-01T01:00:00+01:00')
        self.assertEqual(payload['bbb'], 1500)
        self.assertEqual(payload['ccc'], 0.75)

    @mock.patch('dsmr_mqtt.services.messages.queue_message')
    @mock.patch('django.utils.timezone.now')
    def test_publish_split_topic_gas_consumption(self, now_mock, queue_message_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2020, 1, 1), timezone=timezone.utc
        )
        split_topic_settings = consumption.SplitTopicGasConsumptionMQTTSettings.get_solo()
        gas_consumption = self._create_gas_consumption()

        # Mapping.
        split_topic_settings.formatting = '''
[mapping]
read_at = dsmr/consumption/gas/read_at
delivered = dsmr/consumption/gas/delivered
currently_delivered = dsmr/consumption/gas/currently_delivered
'''
        split_topic_settings.save()

        # Disabled by default.
        self.assertFalse(split_topic_settings.enabled)
        self.assertFalse(queue_message_mock.called)
        dsmr_mqtt.services.callbacks.publish_split_topic_gas_consumption(instance=gas_consumption)
        self.assertFalse(queue_message_mock.called)

        # Now enabled.
        queue_message_mock.reset_mock()
        split_topic_settings.enabled = True
        split_topic_settings.save()
        dsmr_mqtt.services.callbacks.publish_split_topic_gas_consumption(instance=gas_consumption)
        self.assertTrue(queue_message_mock.called)

        called_kwargs = [x[1] for x in queue_message_mock.call_args_list]
        expected = {
            'payload': '2020-01-01T01:00:00+01:00',
            'topic': 'dsmr/consumption/gas/read_at'
        }
        self.assertIn(expected, called_kwargs)
