from django.dispatch import Signal


# Triggered whenever a 'dsmr_backend' management command was called.
backend_called = Signal()

# Triggered when a restart of the process is required.
backend_restart_required = Signal()

# Triggered for persistent client (e.g. MQTT) init and processing.
initialize_persistent_client = Signal()
run_persistent_client = Signal()
terminate_persistent_client = Signal()
