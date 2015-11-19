from django.conf.urls import url

from dsmr_stats.views import Dashboard, History, RecentElectricityData, RecentGasData


urlpatterns = [
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^recent', History.as_view(), name='history'),
    url(r'^power-data$', RecentElectricityData.as_view(), name='recent-electricity-data-json'),
    url(r'^gas-data$', RecentGasData.as_view(), name='recent-gas-data-json'),
]
