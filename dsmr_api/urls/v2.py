from django.conf.urls import include
from django.urls.conf import path

from dsmr_api.views import v2 as views


app_name = 'api-v2'

datalogger_url_patterns = [
    path('dsmrreading', views.DsmrReadingViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='dsmrreading'),
]

consumption_url_patterns = [
    path('electricity', views.ElectricityConsumptionViewSet.as_view({'get': 'list'}), name='electricity-consumption'),
    path('gas', views.GasConsumptionViewSet.as_view({'get': 'list'}), name='gas-consumption'),
    path('today', views.TodayConsumptionView.as_view(), name='today-consumption'),
    path('electricity-live', views.ElectricityLiveView.as_view(), name='electricity-live'),
    path('gas-live', views.GasLiveView.as_view(), name='gas-live'),
]

statistics_url_patterns = [
    path('day', views.DayStatisticsViewSet.as_view({'get': 'list'}), name='day-statistics'),
    path('hour', views.HourStatisticsViewSet.as_view({'get': 'list'}), name='hour-statistics'),
]

application_url_patterns = [
    path('version', views.VersionView.as_view(), name='application-version'),
    path('status', views.StatusView.as_view(), name='application-status'),
]

urlpatterns = [
    path('datalogger/', include(datalogger_url_patterns)),
    path('consumption/', include(consumption_url_patterns)),
    path('statistics/', include(statistics_url_patterns)),
    path('application/', include(application_url_patterns)),
]
