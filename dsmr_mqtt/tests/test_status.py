from django.test import TestCase, override_settings

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_mqtt.apps import check_mqtt_messages_queue
from dsmr_mqtt.models.queue import Message


class TestStatus(TestCase):
    def setUp(self):
        Message.objects.create(topic='test', payload='')
        self.assertEqual(Message.objects.all().count(), 1)

    @override_settings(DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE=2)
    def test_check_mqtt_messages_queue_okay(self):
        self.assertIsNone(check_mqtt_messages_queue())

    @override_settings(DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE=1)
    def test_check_mqtt_messages_queue_fail(self):
        self.assertIsInstance(check_mqtt_messages_queue(), MonitoringStatusIssue)
