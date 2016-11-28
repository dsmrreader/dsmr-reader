from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls import url

from dsmr_frontend.views.dashboard import Dashboard, DashboardXhrHeader
from dsmr_frontend.views.archive import Archive, ArchiveXhrSummary, ArchiveXhrGraphs
from dsmr_frontend.views.statistics import Statistics
from dsmr_frontend.views.trends import Trends
from dsmr_frontend.views.compare import Compare
from dsmr_frontend.views.export import Export, ExportAsCsv
from dsmr_frontend.views.status import Status
from dsmr_frontend.views.notification import NotificationRead
from dsmr_frontend.views.generic import DocsRedirect, FeedbackRedirect


urlpatterns = [
    # Public views.
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^xhr/header$', DashboardXhrHeader.as_view(), name='dashboard-xhr-header'),
    url(r'^archive$', Archive.as_view(), name='archive'),
    url(r'^archive/xhr/summary$', ArchiveXhrSummary.as_view(), name='archive-xhr-summary'),
    url(r'^archive/xhr/graphs$', ArchiveXhrGraphs.as_view(), name='archive-xhr-graphs'),
    url(r'^statistics$', Statistics.as_view(), name='statistics'),
    url(r'^trends$', cache_page(settings.CACHES['default']['TIMEOUT'])(Trends.as_view()), name='trends'),
    url(r'^compare$', Compare.as_view(), name='compare'),

    # Maintainance view.
    url(r'^status$', Status.as_view(), name='status'),

    # Generic redirects to external (help) pages.
    url(r'^docs-redirect$', DocsRedirect.as_view(), name='docs-redirect'),
    url(r'^feedback-redirect$', FeedbackRedirect.as_view(), name='feedback-redirect'),

    # Views requiring authentication.
    url(r'^export$', login_required(Export.as_view()), name='export'),
    url(r'^export/csv$', login_required(ExportAsCsv.as_view()), name='export-as-csv'),

    url(r'^notification-read$', login_required(NotificationRead.as_view()), name='notification-read'),
]
