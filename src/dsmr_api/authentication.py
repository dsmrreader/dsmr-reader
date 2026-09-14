from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions

from dsmr_api.models import APISettings
import dsmr_api.services


class HeaderAuthentication(authentication.BaseAuthentication):
    """
    Authentication is provided by sending the API "key" via a header on each request.
    - 'X-AUTHKEY: key'
    - 'AUTHORIZATION: Token key'

    The API key can be managed inside the admin interface of the application.
    """

    def authenticate(self, request):
        api_settings = APISettings.get_solo()

        if not api_settings.allow:
            raise exceptions.PermissionDenied("API is disabled")

        if not dsmr_api.services.authkey_is_valid(request, api_settings):
            raise exceptions.AuthenticationFailed("Invalid auth key")

        try:
            user = User.objects.get(username=settings.DSMRREADER_REST_FRAMEWORK_API_USER)
        except User.DoesNotExist as exc:
            raise exceptions.APIException("API user not found") from exc

        return user, None
