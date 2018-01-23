from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include('dsmr_api.urls.v1')),
    url(r'^api/v2/', include('dsmr_api.urls.v2')),
    url(r'^', include('dsmr_frontend.urls')),
]

if settings.DEBUG:
    import debug_toolbar  # pragma: no cover

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]  # pragma: no cover
