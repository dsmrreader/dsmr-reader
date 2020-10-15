from django.dispatch import Signal


# Triggered whenever a notification was sent. Use this to relay the same notification to another destination.
notification_sent = Signal()
