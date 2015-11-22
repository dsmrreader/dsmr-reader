from django.conf.urls import url

from dsmr_stats.views import Dashboard, History, Statistics, EnergySupplierPrices, \
    RecentElectricityData, RecentGasData, LatestData


urlpatterns = [
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^history$', History.as_view(), name='history'),
    url(r'^statistics$', Statistics.as_view(), name='statistics'),
    url(r'^energy-supplier-prices$', EnergySupplierPrices.as_view(), name='energy-supplier-prices'),
    url(r'^xhr/power-data$', RecentElectricityData.as_view(), name='recent-electricity-data-json'),
    url(r'^xhr/gas-data$', RecentGasData.as_view(), name='recent-gas-data-json'),
    url(r'^xhr/latest-data$', LatestData.as_view(), name='latest-data-json'),
]
