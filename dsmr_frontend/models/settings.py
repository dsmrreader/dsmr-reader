from adminsortable.models import SortableMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from solo.models import SingletonModel
from colorfield.fields import ColorField

from dsmr_backend.mixins import ModelUpdateMixin


class FrontendSettings(ModelUpdateMixin, SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    GRAPH_STYLE_BAR = 'bar'
    GRAPH_STYLE_LINE = 'line'
    GRAPH_STYLES = (
        (GRAPH_STYLE_BAR, _('Bar')),
        (GRAPH_STYLE_LINE, _('Line')),
    )

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
    live_graphs_hours_range = models.IntegerField(
        default=24,
        validators=[MinValueValidator(1), MaxValueValidator(7 * 24)],
        verbose_name=_('Live graphs hours range'),
        help_text=_("The range of the data displayed in live graphs (increasing it may degrade rendering performance!)")
    )
    live_graphs_initial_zoom = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_('Live graphs initial zoom'),
        help_text=_("The percentage of the graph range displayed initially")
    )
    gas_graph_style = models.CharField(
        max_length=4,
        choices=GRAPH_STYLES,
        default=GRAPH_STYLE_BAR,
        verbose_name=_('Gas graph style'),
        help_text=_("Using the bar style will help you distinguish empty values better")
    )
    electricity_graph_style = models.CharField(
        max_length=4,
        choices=GRAPH_STYLES,
        default=GRAPH_STYLE_BAR,
        verbose_name=_('Electricity graph style'),
        help_text=_("Archive graphs only: Use the bar style to change visualisation")
    )
    stack_electricity_graphs = models.BooleanField(
        default=True,
        verbose_name=_('Stack electricity graphs'),
        help_text=_(
            "Archive graphs only: Stacking, in combination with the bar graph style, distinguishes tariffs better"
        )
    )
    tariff_1_delivered_name = models.CharField(
        max_length=30,
        default='Laagtarief',
        verbose_name=_('Name of tariff 1 (delivered)'),
        help_text=_("Defaults to 'low tariff' delivered")
    )
    tariff_2_delivered_name = models.CharField(
        max_length=30,
        default='Hoogtarief',
        verbose_name=_('Name of tariff 2 (delivered)'),
        help_text=_("Defaults to 'normal tariff' or 'high tariff' delivered")
    )
    tariff_1_returned_name = models.CharField(
        max_length=30,
        default='Laagtarief teruglevering',
        verbose_name=_('Name of tariff 1 (returned)'),
        help_text=_("Defaults to 'low tariff' returned")
    )
    tariff_2_returned_name = models.CharField(
        max_length=30,
        default='Hoogtarief teruglevering',
        verbose_name=_('Name of tariff 2 (returned)'),
        help_text=_("Defaults to 'normal tariff' or 'high tariff' returned")
    )
    always_require_login = models.BooleanField(
        default=False,
        verbose_name=_('Force password login everywhere'),
        help_text=_(
            'Enable this to enforce login on all pages. Useful to restrict unauthorized access when hosted or '
            'reachable on the Internet.'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Frontend configuration')


class SortedGraph(SortableMixin, models.Model):
    name = models.CharField(max_length=64)
    graph_type = models.CharField(max_length=32)
    sorting_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Sorted graph')
        verbose_name_plural = _('Sorted graphs')
        ordering = ['sorting_order']
