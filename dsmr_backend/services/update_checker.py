import logging

from django.utils.translation import gettext_lazy as _
from django.utils import timezone

import dsmr_frontend.services
import dsmr_backend.services.backend
from dsmr_backend.models.schedule import ScheduledProcess


logger = logging.getLogger('dsmrreader')


def run(scheduled_process: ScheduledProcess):
    """ Checks for new updates. If one is available, it's displayed on the Dashboard. """
    try:
        is_latest_version = dsmr_backend.services.backend.is_latest_version()
    except Exception as error:
        logger.error('Update checker: Error %s', error)
        return scheduled_process.delay(timezone.timedelta(hours=1))

    if not is_latest_version:
        logger.debug('Update checker: Newer version of DSMR-reader available')
        dsmr_frontend.services.display_dashboard_message(
            message=_(
                'There is a newer version of DSMR-reader available. See the changelog for more information.'
            ),
            redirect_to='frontend:changelog-redirect'
        )

    scheduled_process.delay(timezone.timedelta(days=7))
