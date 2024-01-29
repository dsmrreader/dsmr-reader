from django.views.generic.base import TemplateView

from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin
from dsmr_frontend.models.settings import FrontendSettings
import dsmr_backend.services.backend
import dsmr_consumption.services


class EnergyContracts(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = "dsmr_frontend/energy-contracts.html"

    def get_context_data(self, **kwargs):
        context_data = super(EnergyContracts, self).get_context_data(**kwargs)

        context_data["capabilities"] = dsmr_backend.services.backend.get_capabilities()
        context_data["frontend_settings"] = FrontendSettings.get_solo()
        context_data["energy_contracts"] = (
            dsmr_consumption.services.summarize_energy_contracts()
        )

        return context_data
