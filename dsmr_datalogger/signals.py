import django.dispatch

raw_telegram = django.dispatch.Signal(providing_args=["data"])
