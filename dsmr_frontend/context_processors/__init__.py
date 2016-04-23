from django.conf import settings


def version(request):
    return {
        'dsmr_version': settings.DSMR_VERSION,
        'LANGUAGE_CODE': request.LANGUAGE_CODE,
    }
