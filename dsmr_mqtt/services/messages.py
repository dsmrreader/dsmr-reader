import hashlib
import logging

from django.conf import settings
from django.core.cache import caches

from dsmr_mqtt.models import queue


logger = logging.getLogger('commands')


def queue_message(topic, payload):
    """
    Queues a new message, but only if it doesn't exist yet and is no cached.

    - Maximum message queue size will be maintained.
    - Duplicate, unsent messages will be ignored.
    - Each message sent will be cached, as it'll be dispatched with the retain flag.
    """

    if queue.Message.objects.all().count() >= settings.DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE:
        return logger.warning('Ignoring %s to max messages in queue reached', topic)

    cache_storage = caches['mqtt']

    cache_key = '{}__{}'.format(topic, payload).encode('utf-8')
    cache_key = hashlib.sha256(cache_key).hexdigest()

    if cache_storage.get(cache_key):
        return logger.debug('Ignoring %s due to cache', topic)

    _, created = queue.Message.objects.get_or_create(topic=topic, payload=payload)

    # We do not care about the value cached, as it's already included in the cache key.
    cache_storage.set(cache_key, True)

    if not created:
        return logger.debug('Ignoring %s due to queue', topic)

    logger.debug('Queued message for %s', topic)
