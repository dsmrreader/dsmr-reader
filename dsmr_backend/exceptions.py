from django.utils import timezone


class DelayNextCall(Exception):
    """ Signals the backend to update the next call timestamp for the current serivce. """
    def __init__(self, timestamp=None, **delta_kwargs):
        """ Either initialize with timedelta kwargs or an exact datetime (as timestamp parameter). """
        if timestamp:
            self.delta = timestamp - timezone.now()
        else:
            self.delta = timezone.timedelta(**delta_kwargs)
