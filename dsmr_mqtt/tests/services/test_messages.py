from unittest import mock

from django.test import TestCase, override_settings

from dsmr_mqtt.models import queue
import dsmr_mqtt.services.messages


class TestMessages(TestCase):
    TOPIC = 'fake-topic'
    PAYLOAD = 'abcde' * 50

    def test_okay(self):
        self.assertFalse(queue.Message.objects.exists())
        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=self.PAYLOAD)
        self.assertTrue(queue.Message.objects.exists())

    @override_settings(DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE=1)
    @mock.patch('django.core.cache.backends.dummy.DummyCache.get')
    def test_max(self, cache_mock):
        # Caching disabled for this test.
        cache_mock.return_value = None

        self.assertEqual(queue.Message.objects.all().count(), 0)
        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=1)
        self.assertEqual(queue.Message.objects.all().count(), 1)

        # Max reached, should be ignored.
        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=2)
        self.assertEqual(queue.Message.objects.all().count(), 1)

    @mock.patch('django.core.cache.backends.dummy.DummyCache.get')
    def test_cached(self, cache_mock):
        cache_mock.return_value = True

        self.assertFalse(queue.Message.objects.exists())
        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=self.PAYLOAD)
        self.assertFalse(queue.Message.objects.exists())

    def test_duplicate(self):
        self.assertEqual(queue.Message.objects.all().count(), 0)

        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=self.PAYLOAD)
        self.assertEqual(queue.Message.objects.all().count(), 1)

        # Second create should be ignored. And caching is disabled in tests as well.
        dsmr_mqtt.services.messages.queue_message(topic=self.TOPIC, payload=self.PAYLOAD)
        self.assertEqual(queue.Message.objects.all().count(), 1)
