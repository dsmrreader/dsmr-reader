from django.views.decorators.cache import cache_page
from django.conf import settings
from django.conf.urls import url

from dsmr_frontend.views.dashboard import Dashboard
from dsmr_frontend.views.history import History
from dsmr_frontend.views.statistics import Statistics

urlpatterns = [
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(
        r'^history$',
        cache_page(settings.CACHES['default']['TIMEOUT'])(History.as_view()),
        name='history'
    ),
    url(r'^statistics$', Statistics.as_view(), name='statistics'),
]
