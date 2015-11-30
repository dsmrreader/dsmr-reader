from django.views.decorators.cache import cache_page
from django.conf import settings
from django.conf.urls import url

from dsmr_stats import views


urlpatterns = [
    url(r'^$', views.Dashboard.as_view(), name='dashboard'),
    url(
        r'^history$',
        cache_page(settings.CACHES['default']['TIMEOUT'])(
            views.History.as_view()
        ),
        name='history'
    ),
    url(
        r'^statistics$',
        views.Statistics.as_view(),
        name='statistics'
    ),
    url(
        r'^energy-supplier-prices$',
        cache_page(settings.CACHES['default']['TIMEOUT'])(
            views.EnergySupplierPrices.as_view()
        ),
        name='energy-supplier-prices'
    ),
]
