"""
Project wide signals used among apps.
"""
from django.dispatch import Signal


# Triggered whenever a new ELECTRICITY consumption model was created and stored to database.
electricity_consumption_created = Signal(providing_args=["instance"])

# Triggered whenever a new GAS consumption model was created and stored to database.
gas_consumption_created = Signal(providing_args=["instance"])

# Triggered whenever a new electricity statistics model was created and stored to database.
electricity_statistics_created = Signal(providing_args=["instance"])
