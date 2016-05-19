from django.http.response import HttpResponseNotAllowed, HttpResponseForbidden,\
    HttpResponseBadRequest, HttpResponseServerError, HttpResponse
from django.views.generic.base import View
from django.utils.translation import ugettext as _

from dsmr_api.models import APISettings
from dsmr_api.forms import DsmrReadingForm
import dsmr_datalogger.services


class DataloggerDsmrReading(View):
    def post(self, request):
        api_settings = APISettings.get_solo()

        # API disabled.
        if not api_settings.allow:
            return HttpResponseNotAllowed(permitted_methods=['POST'], content=_('API is disabled'))

        # Auth key mismatch.
        if request.META.get('HTTP_X_AUTHKEY') != api_settings.auth_key:
            return HttpResponseForbidden(content=_('Invalid auth key'))

        post_form = DsmrReadingForm(request.POST)

        # Data omitted.
        if not post_form.is_valid():
            return HttpResponseBadRequest(_('Invalid data'))

        try:
            dsmr_reading = dsmr_datalogger.services.telegram_to_reading(
                data=post_form.cleaned_data['telegram']
            )
        except:
            dsmr_reading = None

        # Data invalid.
        if not dsmr_reading:
            return HttpResponseServerError(content=_('Failed to parse telegram'))

        return HttpResponse()
