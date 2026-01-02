from django.dispatch import Signal


# Incoming datalogger telegram.
raw_telegram = Signal()

# Datalogger created a new DSMR reading, a somewhat better signal bind instead of the default Django one.
dsmr_reading_created = Signal()

# Triggered when a restart of the process is required.
datalogger_restart_required = Signal()
