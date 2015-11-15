from django.conf.urls import url

from dsmr_stats.views import Dashboard, Recent, PowerData, GasData


urlpatterns = [
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^recent', Recent.as_view(), name='recent'),
    url(r'^power-data$', PowerData.as_view(), name='power-data-json'),
    url(r'^gas-data$', GasData.as_view(), name='gas-data-json'),
]
