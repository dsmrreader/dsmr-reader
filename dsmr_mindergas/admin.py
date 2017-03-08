from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_mindergas.models.settings import MinderGasSettings


@admin.register(MinderGasSettings)
class MinderGasSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('next_export', )
    fieldsets = (
        (
            None, {
                'fields': ['export', 'auth_token', 'next_export'],
                'description': _(
                    'Detailed instructions for configuring MinderGas.nl can be found here: <a href="https://dsmr-reader'
                    '.readthedocs.io/nl/latest/faq.html#mindergas-nl-automated-gas-meter-position-export">'
                    'FAQ in documentation</a>'
                )
            }
        ),
    )
