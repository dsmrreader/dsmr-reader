from django.conf.urls import url

from dsmr_stats.views import Dashboard, History, Statistics, RecentElectricityData, RecentGasData


urlpatterns = [
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^history', History.as_view(), name='history'),
    url(r'^statistics', Statistics.as_view(), name='statistics'),
    url(r'^xhr/power-data$', RecentElectricityData.as_view(), name='recent-electricity-data-json'),
    url(r'^xhr/gas-data$', RecentGasData.as_view(), name='recent-gas-data-json'),
]
