import logging

from dsmr_backend.signals import initialize_persistent_client, run_persistent_client, terminate_persistent_client


logger = logging.getLogger('commands')


def initialize():
    """ Asks listeners to create their clients and return them for persistent during process lifetime. """
    responses = initialize_persistent_client.send_robust(None)
    clients = []

    for current_receiver, current_response in responses:
        if isinstance(current_response, Exception):
            logger.error(
                '(%s) %s errored: %s',
                current_response.__class__.__name__,
                current_receiver,
                current_response
            )
            continue

        if not current_response:
            continue

        # We expect all listeners to return their client instance.
        clients.append(current_response)

    return clients


def run(clients):
    """ Asks listeners to run tasks with their client. """
    logger.debug('CLIENTS: Running %d client(s)', len(clients))

    for current in clients:
        run_persistent_client.send_robust(None, client=current)


def terminate(clients):
    """ Asks listeners to terminate their client. """
    logger.debug('CLIENTS: Terminating %d client(s)', len(clients))

    for current in clients:
        terminate_persistent_client.send_robust(None, client=current)
