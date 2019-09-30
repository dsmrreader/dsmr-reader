from unittest import mock

from django.test import TestCase

from dsmr_mqtt.models import queue
import dsmr_mqtt.services.messages


class TestMessages(TestCase):
    TOPIC = 'fake-topic'
    PAYLOAD = 'abcde' * 50

    def test_okay(self):
        self.assertFalse(queue.Message.objects.exists())
        dsmr_mqtt.services.messages.queue_message(topic=self.PAYLOAD, payload=self.TOPIC)
        self.assertTrue(queue.Message.objects.exists())

    @mock.patch('django.core.cache.backends.dummy.DummyCache.get')
    def test_cached(self, cache_mock):
        cache_mock.return_value = True

        self.assertFalse(queue.Message.objects.exists())
        dsmr_mqtt.services.messages.queue_message(topic=self.PAYLOAD, payload=self.TOPIC)
        self.assertFalse(queue.Message.objects.exists())

    def test_duplicate(self):
        self.assertEqual(queue.Message.objects.all().count(), 0)

        dsmr_mqtt.services.messages.queue_message(topic=self.PAYLOAD, payload=self.TOPIC)
        self.assertEqual(queue.Message.objects.all().count(), 1)

        # Second create should be ignored. And caching is disabled in tests as well.
        dsmr_mqtt.services.messages.queue_message(topic=self.PAYLOAD, payload=self.TOPIC)
        self.assertEqual(queue.Message.objects.all().count(), 1)
