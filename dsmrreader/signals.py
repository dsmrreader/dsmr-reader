"""
Project wide signals used among apps.
"""
from django.dispatch import Signal


electricity_consumption_created = Signal(providing_args=["instance"])
gas_consumption_created = Signal(providing_args=["instance"])
