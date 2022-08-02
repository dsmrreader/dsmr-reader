from django.urls.conf import path

from dsmr_frontend.views.about import About, AboutXhrUpdateCheck, AboutXhrDebugInfo
from dsmr_frontend.views.configuration import Configuration
from dsmr_frontend.views.dashboard import Dashboard
from dsmr_frontend.views.archive import Archive, ArchiveXhrSummary, ArchiveXhrGraphs
from dsmr_frontend.views.docs import RedocApiDocs
from dsmr_frontend.views.notifications import (
    Notifications,
    XhrMarkNotificationRead,
    XhrMarkAllNotificationsRead,
)
from dsmr_frontend.views.statistics import Statistics, StatisticsXhrData
from dsmr_frontend.views.trends import (
    Trends,
    TrendsXhrAvgConsumption,
    TrendsXhrElectricityByTariff,
)
from dsmr_frontend.views.compare import Compare, CompareXhrSummary
from dsmr_frontend.views.export import Export, ExportAsCsv
from dsmr_frontend.views.generic import (
    ChangelogRedirect,
    DocsRedirect,
    FeedbackRedirect,
    DonationsRedirect,
    XhrHeader,
    V5UpgradeRedirect,
    StatusRedirectView,
)
from dsmr_frontend.views.energy_contracts import EnergyContracts
from dsmr_frontend.views.live_graphs import (
    LiveGraphs,
    LiveXhrElectricityConsumption,
    LiveXhrGasConsumption,
    LiveXhrTemperature,
    LiveXhrQuarterHourPeakElectricityConsumption,
)

app_name = "frontend"

urlpatterns = [
    path("", Dashboard.as_view(), name="dashboard"),
    path("live", LiveGraphs.as_view(), name="live-graphs"),
    path("xhr/header", XhrHeader.as_view(), name="xhr-consumption-header"),
    path(
        "xhr/electricity",
        LiveXhrElectricityConsumption.as_view(),
        name="live-xhr-electricity",
    ),
    path(
        "xhr/electricity-peaks",
        LiveXhrQuarterHourPeakElectricityConsumption.as_view(),
        name="live-xhr-electricity-peaks",
    ),
    path("xhr/gas", LiveXhrGasConsumption.as_view(), name="live-xhr-gas"),
    path("xhr/temperature", LiveXhrTemperature.as_view(), name="live-xhr-temperature"),
    path("archive", Archive.as_view(), name="archive"),
    path(
        "archive/xhr/summary", ArchiveXhrSummary.as_view(), name="archive-xhr-summary"
    ),
    path("archive/xhr/graphs", ArchiveXhrGraphs.as_view(), name="archive-xhr-graphs"),
    path("statistics", Statistics.as_view(), name="statistics"),
    path(
        "statistics/xhr/data", StatisticsXhrData.as_view(), name="statistics-xhr-data"
    ),
    path("energy-contracts", EnergyContracts.as_view(), name="energy-contracts"),
    path("trends", Trends.as_view(), name="trends"),
    path(
        "trends/xhr/avg-consumption",
        TrendsXhrAvgConsumption.as_view(),
        name="trends-xhr-avg-consumption",
    ),
    path(
        "trends/xhr/consumption-by-tariff",
        TrendsXhrElectricityByTariff.as_view(),
        name="trends-xhr-consumption-by-tariff",
    ),
    path("compare", Compare.as_view(), name="compare"),
    path(
        "compare/xhr/summary", CompareXhrSummary.as_view(), name="compare-xhr-summary"
    ),
    path("status", StatusRedirectView.as_view(), name="status"),
    path("about", About.as_view(), name="about"),
    path(
        "about/xhr/update-check",
        AboutXhrUpdateCheck.as_view(),
        name="about-xhr-update-check",
    ),
    path(
        "about/xhr/debug-info", AboutXhrDebugInfo.as_view(), name="about-xhr-debug-info"
    ),
    path("notifications", Notifications.as_view(), name="notifications"),
    # Docs.
    path("docs/api/redoc", RedocApiDocs.as_view(), name="redoc-api-docs"),
    # Generic redirects to external (help) pages.
    path("changelog-redirect", ChangelogRedirect.as_view(), name="changelog-redirect"),
    path("docs-redirect", DocsRedirect.as_view(), name="docs-redirect"),
    path("feedback-redirect", FeedbackRedirect.as_view(), name="feedback-redirect"),
    path("donations-redirect", DonationsRedirect.as_view(), name="donations-redirect"),
    path(
        "v5-upgrade-redirect", V5UpgradeRedirect.as_view(), name="v5-upgrade-redirect"
    ),
    # Views always requiring authentication.
    path("configuration", Configuration.as_view(), name="configuration"),
    path("export", Export.as_view(), name="export"),
    path("export/csv", ExportAsCsv.as_view(), name="export-as-csv"),
    path(
        "notifications/xhr/mark-read",
        XhrMarkNotificationRead.as_view(),
        name="notification-xhr-mark-read",
    ),
    path(
        "notifications/xhr/mark-all-read",
        XhrMarkAllNotificationsRead.as_view(),
        name="notification-xhr-mark-all-read",
    ),
]
