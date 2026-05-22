from django.conf import settings
from django.conf.urls import include
from django.urls.conf import path
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView

urlpatterns = [
    path("", include("dsmr_frontend.urls")),
    path("admin/dropbox/", include("dsmr_dropbox.urls")),
    path("admin/", admin.site.urls),
    path("api/v2/schema", SpectacularAPIView.as_view(), name="v2-api-openapi-schema"),
    path("api/v1/", include("dsmr_api.urls.v1")),
    path("api/v2/", include("dsmr_api.urls.v2")),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls  # pragma: no cover

    urlpatterns += debug_toolbar_urls()  # pragma: no cover
