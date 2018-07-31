from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models.settings import FrontendSettings


@admin.register(FrontendSettings)
class FrontendSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            _('Interface'), {
                'fields': ['merge_electricity_tariffs', 'dashboard_graph_width'],
            }
        ),
        (
            _('Electricity delivered'), {
                'fields': [
                    'electricity_delivered_color',
                    'electricity_delivered_alternate_color',
                ],
            }
        ),
        (
            _('Electricity returned'), {
                'fields': [
                    'electricity_returned_color',
                    'electricity_returned_alternate_color',

                ],
            }
        ),
        (
            _('Gas'), {
                'fields': [
                    'gas_delivered_color',
                ],
            }
        ),
        (
            _('Phases P+'), {
                'fields': [
                    'phase_delivered_l1_color',
                    'phase_delivered_l2_color',
                    'phase_delivered_l3_color',
                ],
            }
        ),
        (
            _('Phases P-'), {
                'fields': [
                    'phase_returned_l1_color',
                    'phase_returned_l2_color',
                    'phase_returned_l3_color',
                ],
            }
        ),
        (
            _('Temperature'), {
                'fields': [
                    'temperature_color',
                ],
            }
        ),
    )
