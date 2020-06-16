from django.contrib.auth.mixins import AccessMixin

from dsmr_frontend.models.settings import FrontendSettings


class ConfigurableLoginRequiredMixin(AccessMixin):
    """ Applies logic similar to the LoginRequiredMixin but depending on a configurable setting. """
    def dispatch(self, request, *args, **kwargs):
        if not FrontendSettings.get_solo().always_require_login:
            return super().dispatch(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return super().handle_no_permission()

        return super().dispatch(request, *args, **kwargs)
