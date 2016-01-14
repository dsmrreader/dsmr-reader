"""
Project wide signals used among apps.
"""
from django.dispatch import Signal


gas_consumption_created = Signal(providing_args=["instance"])
