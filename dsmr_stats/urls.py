from django.conf.urls import url

from dsmr_stats.views import Home


urlpatterns = [
    url(r'^$', Home.as_view(), name='home')
]
