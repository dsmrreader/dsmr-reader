import logging

from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backend.signals import backend_called

logger = logging.getLogger('commands')


def dispatch_signals():
    """ Legacy execution, using signals. """
    # send_robust() guarantees the every listener receives this signal.
    responses = backend_called.send_robust(None)

    for __, current_response in responses:
        if isinstance(current_response, Exception):
            logger.exception(current_response)


def execute_scheduled_processes():
    """ Calls the backend and all services required. """
    calls = ScheduledProcess.objects.ready()
    logger.debug('SP: %s backend service(s) ready to run', len(calls))

    for current in calls:
        logger.debug('SP: Running "%s" (%s)', current.name, current.module)

        try:
            current.execute()
        except Exception as error:
            logger.exception(error)

            # Do not hammer.
            current.delay(timezone.timedelta(seconds=30))
