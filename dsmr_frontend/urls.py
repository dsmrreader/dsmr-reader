from django.conf.urls import url

from dsmr_frontend.views.dashboard import Dashboard, DashboardXhrHeader, DashboardXhrConsumption, \
    DashboardXhrNotificationRead, DashboardXhrElectricityConsumption, DashboardXhrGasConsumption, \
    DashboardXhrTemperature
from dsmr_frontend.views.archive import Archive, ArchiveXhrSummary, ArchiveXhrGraphs
from dsmr_frontend.views.statistics import Statistics, StatisticsXhrData
from dsmr_frontend.views.trends import Trends, TrendsXhrAvgConsumption, TrendsXhrElectricityByTariff
from dsmr_frontend.views.compare import Compare
from dsmr_frontend.views.export import Export, ExportAsCsv
from dsmr_frontend.views.status import Status, XhrUpdateChecker
from dsmr_frontend.views.generic import ChangelogRedirect, DocsRedirect, FeedbackRedirect, DonationsRedirect
from dsmr_frontend.views.energy_contracts import EnergyContracts


app_name = 'frontend'

urlpatterns = [
    # Public views.
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^xhr/header$', DashboardXhrHeader.as_view(), name='dashboard-xhr-header'),
    url(r'^xhr/consumption', DashboardXhrConsumption.as_view(), name='dashboard-xhr-consumption'),
    url(r'^xhr/electricity', DashboardXhrElectricityConsumption.as_view(), name='dashboard-xhr-electricity'),
    url(r'^xhr/gas', DashboardXhrGasConsumption.as_view(), name='dashboard-xhr-gas'),
    url(r'^xhr/temperature', DashboardXhrTemperature.as_view(), name='dashboard-xhr-temperature'),
    url(r'^xhr/notification-read$', DashboardXhrNotificationRead.as_view(), name='dashboard-xhr-notification-read'),
    url(r'^archive$', Archive.as_view(), name='archive'),
    url(r'^archive/xhr/summary$', ArchiveXhrSummary.as_view(), name='archive-xhr-summary'),
    url(r'^archive/xhr/graphs$', ArchiveXhrGraphs.as_view(), name='archive-xhr-graphs'),
    url(r'^statistics$', Statistics.as_view(), name='statistics'),
    url(r'^statistics/xhr/data$', StatisticsXhrData.as_view(), name='statistics-xhr-data'),
    url(r'^energy-contracts$', EnergyContracts.as_view(), name='energy-contracts'),
    url(r'^trends$', Trends.as_view(), name='trends'),
    url(r'^trends/xhr/avg-consumption$', TrendsXhrAvgConsumption.as_view(), name='trends-xhr-avg-consumption'),
    url(
        r'^trends/xhr/consumption-by-tariff$',
        TrendsXhrElectricityByTariff.as_view(),
        name='trends-xhr-consumption-by-tariff'
    ),
    url(r'^compare$', Compare.as_view(), name='compare'),

    # Technical information.
    url(r'^status$', Status.as_view(), name='status'),
    url(r'^status/xhr/check-for-updates$', XhrUpdateChecker.as_view(), name='status-xhr-check-for-updates'),

    # Generic redirects to external (help) pages.
    url(r'^changelog-redirect$', ChangelogRedirect.as_view(), name='changelog-redirect'),
    url(r'^docs-redirect$', DocsRedirect.as_view(), name='docs-redirect'),
    url(r'^feedback-redirect$', FeedbackRedirect.as_view(), name='feedback-redirect'),
    url(r'^donations-redirect$', DonationsRedirect.as_view(), name='donations-redirect'),

    # Views requiring authentication.
    url(r'^export$', Export.as_view(), name='export'),
    url(r'^export/csv$', ExportAsCsv.as_view(), name='export-as-csv'),
]
