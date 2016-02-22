from django.views.decorators.cache import cache_page
from django.conf import settings
from django.conf.urls import url

from dsmr_frontend.views.dashboard import Dashboard
from dsmr_frontend.views.history import History
from dsmr_frontend.views.archive import Archive, ArchiveXhr
from dsmr_frontend.views.statistics import Statistics
from dsmr_frontend.views.trends import Trends
from dsmr_frontend.views.status import Status


urlpatterns = [
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(
        r'^history$',
        cache_page(settings.CACHES['default']['TIMEOUT'])(History.as_view()),
        name='history'
    ),
    url(r'^archive$', Archive.as_view(), name='archive'),
    url(r'^archive/xhr$', ArchiveXhr.as_view(), name='archive-xhr'),
    url(r'^statistics$', Statistics.as_view(), name='statistics'),
    url(
        r'^trends$',
        cache_page(settings.CACHES['default']['TIMEOUT'])(Trends.as_view()),
        name='trends'
    ),
    url(r'^status$', Status.as_view(), name='status'),
]
