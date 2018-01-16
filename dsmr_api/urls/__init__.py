from django.conf.urls import include, url


app_name = 'api'
urlpatterns = [
    url(r'^v1/', include('dsmr_api.urls.v1')),  # Remote datalogger only.
    url(r'^v2/', include('dsmr_api.urls.v2')),  # RESTful API.
]
