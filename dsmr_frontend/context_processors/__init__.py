from django.conf import settings


def version(request):
    return {
        'dsmr_version': settings.DSMRREADER_VERSION,
        'DSMRREADER_MAIN_BRANCH': settings.DSMRREADER_MAIN_BRANCH,
        'LANGUAGE_CODE': request.LANGUAGE_CODE,
    }
