from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_mqtt.models.queue import Message


class TestMessage(TestCase):
    """Tests for settings defaults."""

    def setUp(self):
        self.instance = Message.objects.create(topic="x", payload="y")

    def test_admin(self):
        """Model should be registered in Django Admin."""
        self.assertTrue(site.is_registered(Message))
