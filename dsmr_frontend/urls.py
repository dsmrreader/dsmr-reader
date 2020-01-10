from django.urls.conf import path

from dsmr_frontend.views.dashboard import Dashboard, DashboardXhrHeader, DashboardXhrConsumption, \
    DashboardXhrElectricityConsumption, DashboardXhrGasConsumption, DashboardXhrTemperature
from dsmr_frontend.views.archive import Archive, ArchiveXhrSummary, ArchiveXhrGraphs
from dsmr_frontend.views.notifications import Notifications, XhrMarkNotificationRead, XhrMarkAllNotificationsRead
from dsmr_frontend.views.statistics import Statistics, StatisticsXhrData
from dsmr_frontend.views.trends import Trends, TrendsXhrAvgConsumption, TrendsXhrElectricityByTariff
from dsmr_frontend.views.compare import Compare, CompareXhrSummary
from dsmr_frontend.views.export import Export, ExportAsCsv
from dsmr_frontend.views.status import Status, XhrUpdateChecker
from dsmr_frontend.views.generic import ChangelogRedirect, DocsRedirect, FeedbackRedirect, DonationsRedirect
from dsmr_frontend.views.energy_contracts import EnergyContracts


app_name = 'frontend'

# Public views.
urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('xhr/header', DashboardXhrHeader.as_view(), name='dashboard-xhr-header'),
    path('xhr/consumption', DashboardXhrConsumption.as_view(), name='dashboard-xhr-consumption'),
    path('xhr/electricity', DashboardXhrElectricityConsumption.as_view(), name='dashboard-xhr-electricity'),
    path('xhr/gas', DashboardXhrGasConsumption.as_view(), name='dashboard-xhr-gas'),
    path('xhr/temperature', DashboardXhrTemperature.as_view(), name='dashboard-xhr-temperature'),
    path('archive', Archive.as_view(), name='archive'),
    path('archive/xhr/summary', ArchiveXhrSummary.as_view(), name='archive-xhr-summary'),
    path('archive/xhr/graphs', ArchiveXhrGraphs.as_view(), name='archive-xhr-graphs'),
    path('statistics', Statistics.as_view(), name='statistics'),
    path('statistics/xhr/data', StatisticsXhrData.as_view(), name='statistics-xhr-data'),
    path('energy-contracts', EnergyContracts.as_view(), name='energy-contracts'),
    path('trends', Trends.as_view(), name='trends'),
    path('trends/xhr/avg-consumption', TrendsXhrAvgConsumption.as_view(), name='trends-xhr-avg-consumption'),
    path(
        'trends/xhr/consumption-by-tariff',
        TrendsXhrElectricityByTariff.as_view(),
        name='trends-xhr-consumption-by-tariff'
    ),
    path('compare', Compare.as_view(), name='compare'),
    path('compare/xhr/summary', CompareXhrSummary.as_view(), name='compare-xhr-summary'),

    path('status', Status.as_view(), name='status'),
    path('status/xhr/check-for-updates', XhrUpdateChecker.as_view(), name='status-xhr-check-for-updates'),


    # Generic redirects to external (help) pages.
    path('changelog-redirect', ChangelogRedirect.as_view(), name='changelog-redirect'),
    path('docs-redirect', DocsRedirect.as_view(), name='docs-redirect'),
    path('feedback-redirect', FeedbackRedirect.as_view(), name='feedback-redirect'),
    path('donations-redirect', DonationsRedirect.as_view(), name='donations-redirect'),

    # Views requiring authentication.
    path('export', Export.as_view(), name='export'),
    path('export/csv', ExportAsCsv.as_view(), name='export-as-csv'),
    path('notifications', Notifications.as_view(), name='notifications'),
    path('notifications/xhr/mark-read', XhrMarkNotificationRead.as_view(), name='notification-xhr-mark-read'),
    path(
        'notifications/xhr/mark-all-read',
        XhrMarkAllNotificationsRead.as_view(),
        name='notification-xhr-mark-all-read'
    ),
]
