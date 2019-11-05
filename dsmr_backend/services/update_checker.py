import logging

from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

import dsmr_frontend.services
import dsmr_backend.services.backend


logger = logging.getLogger('commands')


def run(scheduled_process):
    """ Creates a new statistics backup and sends it per email. """
    if not dsmr_backend.services.backend.is_latest_version():
        logger.debug('Update checker: Newer version of DSMR-reader available')
        dsmr_frontend.services.display_dashboard_message(message=_(
                'There is a newer version of DSMR-reader available. See the changelog for more information.'
            ),
            redirect_to='frontend:changelog-redirect'
        )

    scheduled_process.delay(timezone.timedelta(days=7))
