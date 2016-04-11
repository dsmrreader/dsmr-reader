from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.conf.urls import url

from dsmr_frontend.views.dashboard import Dashboard
from dsmr_frontend.views.archive import Archive, ArchiveXhrSummary, ArchiveXhrGraphs
from dsmr_frontend.views.statistics import Statistics
from dsmr_frontend.views.trends import Trends
from dsmr_frontend.views.status import Status
from dsmr_frontend.views.configuration import Configuration
from dsmr_frontend.views.deploy import Deploy, DeploymentStream


urlpatterns = [
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^archive$', Archive.as_view(), name='archive'),
    url(r'^archive/xhr/summary$', ArchiveXhrSummary.as_view(), name='archive-xhr-summary'),
    url(r'^archive/xhr/graphs$', ArchiveXhrGraphs.as_view(), name='archive-xhr-graphs'),
    url(r'^statistics$', Statistics.as_view(), name='statistics'),
    url(
        r'^trends$',
        cache_page(settings.CACHES['default']['TIMEOUT'])(Trends.as_view()),
        name='trends'
    ),
    url(r'^status$', Status.as_view(), name='status'),
    url(r'^configuration$', Configuration.as_view(), name='configuration'),
    url(r'^deploy$', login_required(Deploy.as_view()), name='deploy'),
    url(r'^deploy/stream$', login_required(DeploymentStream.as_view()), name='deployment-stream'),
]
