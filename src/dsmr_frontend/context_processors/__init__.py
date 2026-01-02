from django.conf import settings

import dsmr_backend.services.backend


def version(request):
    return {
        "dsmr_version": settings.DSMRREADER_VERSION,
        "monitoring_status_issues": dsmr_backend.services.backend.request_cached_monitoring_status(),
        "DSMRREADER_MAIN_BRANCH": settings.DSMRREADER_MAIN_BRANCH,
        "LANGUAGE_CODE": request.LANGUAGE_CODE,
    }
