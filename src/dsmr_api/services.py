import hmac

from django.http import HttpRequest

from dsmr_api.models import APISettings


def authkey_is_valid(request: HttpRequest, api_settings: APISettings) -> bool:
    """Verifies the API auth key sent in the request headers, using a constant-time comparison."""
    if not api_settings.auth_key:
        return False

    x_authkey_valid = hmac.compare_digest(request.META.get("HTTP_X_AUTHKEY", ""), api_settings.auth_key)
    authorization_valid = hmac.compare_digest(
        request.META.get("HTTP_AUTHORIZATION", ""), "Token {}".format(api_settings.auth_key)
    )

    return x_authkey_valid or authorization_valid
