import logging
from typing import List

from dsmr_backend.signals import (
    initialize_persistent_client,
    run_persistent_client,
    terminate_persistent_client,
)


logger = logging.getLogger("dsmrreader")


def initialize() -> List[object]:
    """Asks listeners to create their clients and return them for persistent during process lifetime."""
    responses = initialize_persistent_client.send_robust(None)
    clients = []

    for _current_receiver, current_response in responses:
        if isinstance(current_response, Exception):
            logger.error("CLIENTS: Init error: %s", current_response)
            continue

        if not current_response:
            continue

        # We expect all listeners to return their client instance.
        clients.append(current_response)

    return clients


def run(clients) -> None:
    """Asks listeners to run tasks with their client."""
    logger.debug("CLIENTS: Running %d active client(s)", len(clients))

    for current in clients:
        responses = run_persistent_client.send_robust(None, client=current)

        for _current_receiver, current_response in responses:
            if isinstance(current_response, Exception):
                logger.error("CLIENTS: Run error: %s", current_response)


def terminate(clients) -> None:
    """Asks listeners to terminate their client."""
    logger.debug("CLIENTS: Terminating %d client(s)", len(clients))

    for current in clients:
        responses = terminate_persistent_client.send_robust(None, client=current)

        for _current_receiver, current_response in responses:
            if isinstance(current_response, Exception):
                logger.exception(current_response)
