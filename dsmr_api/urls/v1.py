from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from dsmr_api.views.v1 import DataloggerDsmrReading


app_name = 'api-v1'

urlpatterns = [
    url(r'^datalogger/dsmrreading$', csrf_exempt(DataloggerDsmrReading.as_view()), name='datalogger-dsmrreading'),
]
