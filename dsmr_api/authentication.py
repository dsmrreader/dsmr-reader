from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions

from dsmr_api.models import APISettings


class HeaderAuthentication(authentication.BaseAuthentication):
    """
    Authentication is provided by sending the API key via a 'X-AUTHKEY' header on each request.
    The API key can be found (and changed) inside the admin interface of the application.
    """
    def authenticate(self, request):
        api_settings = APISettings.get_solo()

        if not api_settings.allow:
            raise exceptions.PermissionDenied('API is disabled')

        if request.META.get('HTTP_X_AUTHKEY') != api_settings.auth_key:
            raise exceptions.AuthenticationFailed('Invalid auth key')

        try:
            user = User.objects.get(username=settings.DSMRREADER_REST_FRAMEWORK_API_USER)
        except User.DoesNotExist:
            raise exceptions.APIException('API user not found')

        return (user, None)
