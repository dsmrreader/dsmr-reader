from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('dsmr_api.urls')),
    url(r'^', include('dsmr_frontend.urls', namespace='frontend')),
]

if settings.DEBUG:
    import debug_toolbar  # pragma: no cover

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]  # pragma: no cover
