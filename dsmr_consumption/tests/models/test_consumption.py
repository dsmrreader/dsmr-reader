from django.test import TestCase
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption


class TestElectricityConsumption(TestCase):
    def setUp(self):
        self.instance = ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=2,
            returned_1=2,
            delivered_2=4,
            returned_2=4,
            currently_delivered=20,
            currently_returned=40,
        )

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'ElectricityConsumption')

    def test_sub(self):
        """ Custom substraction operator. """
        ec1 = ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=1,
            returned_1=2,
            delivered_2=3,
            returned_2=4,
            currently_delivered=0,
            currently_returned=0,
        )
        ec2 = ElectricityConsumption.objects.create(
            read_at=timezone.now() + timezone.timedelta(minutes=1),
            delivered_1=10,
            returned_1=15,
            delivered_2=20,
            returned_2=25,
            currently_delivered=0,
            currently_returned=0,
        )
        diff = ec2 - ec1

        self.assertEqual(diff['delivered_1'], 9)
        self.assertEqual(diff['delivered_2'], 17)
        self.assertEqual(diff['returned_1'], 13)
        self.assertEqual(diff['returned_2'], 21)


class TestGasConsumption(TestCase):
    def setUp(self):
        self.instance = GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=100,
            currently_delivered=1,
        )

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'GasConsumption')
