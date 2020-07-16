from django.dispatch import Signal


# Triggered whenever a 'dsmr_backend' management command was called.
backend_called = Signal(providing_args=[])

# Triggered when a restart of the process is required.
backend_restart_required = Signal(providing_args=[])

# Triggered for persistent client (e.g. MQTT) init and processing.
initialize_persistent_client = Signal(providing_args=[])
run_persistent_client = Signal(providing_args=['client'])
terminate_persistent_client = Signal(providing_args=['client'])
