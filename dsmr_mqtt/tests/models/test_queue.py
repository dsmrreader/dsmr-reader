from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_mqtt.models.queue import Message


class TestMessage(TestCase):
    """ Tests for defaults. """
    def setUp(self):
        self.instance = Message.objects.create(topic='x', payload='y')

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(Message))

    def test_to_string(self):
        self.assertEqual(str(self.instance), '{}'.format(self.instance.topic))

    def test_null_payload(self):
        """ This caused many headaches in issue #515. """
        Message.objects.create(topic='x', payload=None)
