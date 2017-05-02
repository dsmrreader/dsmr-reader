import logging

from django.http.response import HttpResponseNotAllowed, HttpResponseForbidden,\
    HttpResponseBadRequest, HttpResponseServerError, HttpResponse
from django.views.generic.base import View

from dsmr_datalogger.exceptions import InvalidTelegramError
from dsmr_api.models import APISettings
from dsmr_api.forms import DsmrReadingForm
import dsmr_datalogger.services


logger = logging.getLogger('dsmrreader')


class DataloggerDsmrReading(View):
    def post(self, request):
        api_settings = APISettings.get_solo()

        if not api_settings.allow:
            return HttpResponseNotAllowed(permitted_methods=['POST'], content='API is disabled')

        if request.META.get('HTTP_X_AUTHKEY') != api_settings.auth_key:
            return HttpResponseForbidden(content='Invalid auth key')

        post_form = DsmrReadingForm(request.POST)

        if not post_form.is_valid():
            logger.warning('API validation failed with POST data: {}'.format(request.POST))
            return HttpResponseBadRequest('Invalid data')

        dsmr_reading = None

        try:
            dsmr_reading = dsmr_datalogger.services.telegram_to_reading(data=post_form.cleaned_data['telegram'])
        except InvalidTelegramError:
            # The service called already logs the error.
            pass

        if not dsmr_reading:
            return HttpResponseServerError(content='Failed to parse telegram')

        return HttpResponse(status=201)
