from django.contrib.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from adminsortable.admin import SortableAdmin
from solo.admin import SingletonModelAdmin

from dsmr_backend.mixins import ChangeOnlyAdminModel
from .models.message import Notification
from .models.settings import FrontendSettings, SortedGraph


@admin.register(FrontendSettings)
class FrontendSettingsAdmin(SingletonModelAdmin):
    save_on_top = True
    fieldsets = (
        (
            _("Security"),
            {
                "fields": ["always_require_login"],
            },
        ),
        (
            _("Interface"),
            {
                "fields": [
                    "frontend_theme",
                    "gui_refresh_interval",
                    "merge_electricity_tariffs",
                ],
            },
        ),
        (
            _("Graphs"),
            {
                "fields": [
                    "live_graphs_initial_zoom",
                    "live_graphs_hours_range",
                    "electricity_graph_style",
                    "stack_electricity_graphs",
                    "gas_graph_style",
                ],
            },
        ),
        (
            _("Tariff names"),
            {
                "fields": [
                    "tariff_1_delivered_name",
                    "tariff_2_delivered_name",
                    "tariff_1_returned_name",
                    "tariff_2_returned_name",
                ],
            },
        ),
        (
            _("Electricity delivered"),
            {
                "fields": [
                    "electricity_delivered_color",
                    "electricity_delivered_alternate_color",
                ],
            },
        ),
        (
            _("Electricity returned"),
            {
                "fields": [
                    "electricity_returned_color",
                    "electricity_returned_alternate_color",
                ],
            },
        ),
        (
            _("Gas"),
            {
                "fields": [
                    "gas_delivered_color",
                ],
            },
        ),
        (
            _("Phases P+"),
            {
                "fields": [
                    "phase_delivered_l1_color",
                    "phase_delivered_l2_color",
                    "phase_delivered_l3_color",
                ],
            },
        ),
        (
            _("Phases P-"),
            {
                "fields": [
                    "phase_returned_l1_color",
                    "phase_returned_l2_color",
                    "phase_returned_l3_color",
                ],
            },
        ),
        (
            _("Temperature"),
            {
                "fields": [
                    "temperature_color",
                ],
            },
        ),
    )


@admin.register(Notification)
class FrontendNotificationAdmin(ModelAdmin):
    ordering = ["-read"]
    list_display = (
        "message",
        "read",
    )


@admin.register(SortedGraph)
class SortedGraphAdmin(ChangeOnlyAdminModel, SortableAdmin):
    list_display = ("sorting_order", "name", "graph_type")
    fieldsets = (
        (
            None,
            {
                "fields": ["sorting_order", "name"],
                "description": _(
                    "To alter the order in which the graphs are displayed, "
                    '<a href="/admin/dsmr_frontend/sortedgraph/sort/">go to this page</a> and drag the graph names.'
                ),
            },
        ),
    )
