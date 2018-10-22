from django.views.decorators.csrf import csrf_exempt
from django.urls.conf import path

from dsmr_api.views.v1 import DataloggerDsmrReading


app_name = 'api-v1'

urlpatterns = [
    path('datalogger/dsmrreading', csrf_exempt(DataloggerDsmrReading.as_view()), name='datalogger-dsmrreading'),
]
