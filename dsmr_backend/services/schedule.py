import logging

from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backend.signals import backend_called


logger = logging.getLogger('dsmrreader')


def dispatch_signals():
    """ Legacy execution, using signals. """
    # send_robust() guarantees the every listener receives this signal.
    responses = backend_called.send_robust(None)

    for current_receiver, current_response in responses:
        if isinstance(current_response, Exception):
            logger.error(
                '(%s) %s errored: %s',
                current_response.__class__.__name__,
                current_receiver,
                current_response
            )


def execute_scheduled_processes():
    """ Calls the backend and all services required. """
    calls = ScheduledProcess.objects.ready()
    logger.debug('SP: %s backend service(s) ready to run', len(calls))

    for current in calls:
        logger.debug('SP: Running "%s" (%s)', current.name, current.module)

        try:
            current.execute()
        except Exception as error:
            logger.error(
                '(%s) %s errored: %s',
                error.__class__.__name__,
                current.module,
                error
            )

            # Do not hammer.
            current.delay(timezone.timedelta(seconds=30))
