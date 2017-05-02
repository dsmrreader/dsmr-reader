from django.conf.urls import include, url


urlpatterns = [
    url(r'^v1/', include('dsmr_api.urls.v1', namespace='api-v1')),  # Remote datalogger only.
    url(r'^v2/', include('dsmr_api.urls.v2', namespace='api-v2')),  # RESTful API.
]
