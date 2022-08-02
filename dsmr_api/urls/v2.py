from django.conf.urls import include
from django.urls.conf import path

from dsmr_api.views import v2 as views

app_name = "api-v2"

datalogger_url_patterns = [
    path(
        "dsmrreading",
        views.DsmrReadingViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="dsmrreading",
    ),
    path(
        "meter-statistics",
        views.MeterStatisticsViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
            }
        ),
        name="meter-statistics",
    ),
]

consumption_url_patterns = [
    path(
        "energy-supplier-prices",
        views.EnergySupplierPriceViewSet.as_view({"get": "list"}),
        name="energy-supplier-price",
    ),
    path(
        "electricity",
        views.ElectricityConsumptionViewSet.as_view({"get": "list"}),
        name="electricity-consumption",
    ),
    path(
        "electricity-live", views.ElectricityLiveView.as_view(), name="electricity-live"
    ),
    path(
        "gas",
        views.GasConsumptionViewSet.as_view({"get": "list"}),
        name="gas-consumption",
    ),
    path("gas-live", views.GasLiveView.as_view(), name="gas-live"),
    path("today", views.TodayConsumptionView.as_view(), name="today-consumption"),
]

statistics_url_patterns = [
    path(
        "day",
        views.DayStatisticsViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="day-statistics",
    ),
    path(
        "hour",
        views.HourStatisticsViewSet.as_view({"get": "list"}),
        name="hour-statistics",
    ),
]

application_url_patterns = [
    path("version", views.VersionView.as_view(), name="application-version"),
    path(
        "monitoring",
        views.MonitoringIssuesView.as_view(),
        name="application-monitoring",
    ),
]

urlpatterns = [
    path("datalogger/", include(datalogger_url_patterns)),
    path("consumption/", include(consumption_url_patterns)),
    path("statistics/", include(statistics_url_patterns)),
    path("application/", include(application_url_patterns)),
]
