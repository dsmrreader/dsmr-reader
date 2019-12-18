from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _
from django.db import models
from solo.models import SingletonModel
from colorfield.fields import ColorField

from dsmr_backend.mixins import ModelUpdateMixin


class FrontendSettings(ModelUpdateMixin, SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    merge_electricity_tariffs = models.BooleanField(
        default=False,
        verbose_name=_('Merge electricity tariffs'),
        help_text=_('Whether you are using a single electricity tariff and both (high/low) should be displayed merged')
    )

    electricity_delivered_color = ColorField(
        default='#F05050',
        verbose_name=_('Electricity delivered color'),
        help_text=_("Graph color for electricity delivered (default + high tariff)")
    )
    electricity_delivered_alternate_color = ColorField(
        default='#7D311A',
        verbose_name=_('Electricity delivered color (alternative)'),
        help_text=_("Graph color for electricity delivered (low tariff)")
    )
    electricity_returned_color = ColorField(
        default='#27C24C',
        verbose_name=_('Electricity returned color'),
        help_text=_("Graph color for electricity returned (default + high tariff)")
    )
    electricity_returned_alternate_color = ColorField(
        default='#C8C864',
        verbose_name=_('Electricity returned color (alternative)'),
        help_text=_("Graph color for electricity returned (low tariff)")
    )
    gas_delivered_color = ColorField(
        default='#FF851B',
        verbose_name=_('Gas delivered color'),
        help_text=_("Graph color for gas delivered")
    )
    phase_delivered_l1_color = ColorField(
        default='#A47448',
        verbose_name=_('Phase L1+ (delivered) color'),
        help_text=_("Graph color for phase L1+")
    )
    phase_delivered_l2_color = ColorField(
        default='#A4484E',
        verbose_name=_('Phase L2+ (delivered) color'),
        help_text=_("Graph color for phase L2+ (when available)")
    )
    phase_delivered_l3_color = ColorField(
        default='#A44882',
        verbose_name=_('Phase L3+ (delivered) color'),
        help_text=_("Graph color for phase L3+ (when available)")
    )
    phase_returned_l1_color = ColorField(
        default='#2E7D32',
        verbose_name=_('Phase L1- (returned) color'),
        help_text=_("Graph color for phase L1-")
    )
    phase_returned_l2_color = ColorField(
        default='#8BC34A',
        verbose_name=_('Phase L2- (returned) color'),
        help_text=_("Graph color for phase L2- (when available)")
    )
    phase_returned_l3_color = ColorField(
        default='#9E9D24',
        verbose_name=_('Phase L3- (returned) color'),
        help_text=_("Graph color for phase L3- (when available)")
    )
    temperature_color = ColorField(
        default='#0073B7',
        verbose_name=_('Temperature color'),
        help_text=_("Graph color for temperatures read")
    )
    dashboard_graph_width = models.IntegerField(
        default=30,
        validators=[MinValueValidator(30), MaxValueValidator(60 * 60 * 24)],
        verbose_name=_('Dashboard graph width'),
        help_text=_("The number of items displayed on the X-axis of the dashboard graphs")
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Frontend configuration')
