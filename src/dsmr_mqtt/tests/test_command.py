from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_mqtt.models import queue


class TestCommand(InterceptCommandStdoutMixin, TestCase):
    def test_dsmr_mqtt_clear_queue(self):
        queue.Message.objects.create(topic="z", payload="y")
        self.assertEqual(queue.Message.objects.all().count(), 1)

        self._intercept_command_stdout("dsmr_mqtt_clear_queue")

        self.assertEqual(queue.Message.objects.all().count(), 0)
