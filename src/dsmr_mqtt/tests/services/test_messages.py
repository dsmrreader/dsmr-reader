from unittest import mock

from django.test import TestCase, override_settings

from dsmr_mqtt.models import queue
import dsmr_mqtt.services.messages


class TestMessages(TestCase):
    TOPIC = "fake-topic"
    PAYLOAD = "abcde" * 50
    DIFFERENT_PAYLOAD = "xyz"

    def test_okay(self):
        self.assertFalse(queue.Message.objects.exists())
        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=self.PAYLOAD)
        self.assertTrue(queue.Message.objects.exists())

    @override_settings(DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE=1)
    @mock.patch("dsmr_mqtt.services.messages.caches")
    def test_max(self, mock_caches):
        # Caching disabled for this test.
        mock_cache = mock.MagicMock()
        mock_cache.get.return_value = None
        mock_caches.__getitem__.return_value = mock_cache

        self.assertEqual(queue.Message.objects.all().count(), 0)
        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=self.PAYLOAD)
        self.assertEqual(queue.Message.objects.all().count(), 1)

        # Max reached, should be ignored.
        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=self.DIFFERENT_PAYLOAD)
        self.assertEqual(queue.Message.objects.all().count(), 1)

    @mock.patch("dsmr_mqtt.services.messages.caches")
    def test_cached(self, mock_caches):
        mock_cache = mock.MagicMock()
        mock_cache.get.return_value = self.PAYLOAD
        mock_caches.__getitem__.return_value = mock_cache

        # Same topic/payload should block message.
        self.assertFalse(queue.Message.objects.exists())
        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=self.PAYLOAD)
        self.assertFalse(queue.Message.objects.exists())

        # Different payload for the same topic should be allowed
        mock_cache.set.reset_mock()
        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=self.DIFFERENT_PAYLOAD)
        self.assertTrue(queue.Message.objects.exists())

        # Cache should be updated with new value.
        calls = mock_cache.set.call_args_list[0][0]
        self.assertIn(self.TOPIC, calls)
        self.assertIn(self.DIFFERENT_PAYLOAD, calls)
        self.assertNotIn(self.PAYLOAD, calls)
