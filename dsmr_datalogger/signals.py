import django.dispatch

# Incoming datalogger telegram.
raw_telegram = django.dispatch.Signal(providing_args=["data"])

# Datalogger created a new DSMR reading, a somewhat better signal bind instead of the default Django one.
dsmr_reading_created = django.dispatch.Signal(providing_args=["instance"])
