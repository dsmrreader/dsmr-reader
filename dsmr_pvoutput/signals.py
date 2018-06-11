from django.dispatch import Signal


# Triggered whenever a PVOutput upload is performed.
pvoutput_upload = Signal(providing_args=[])
