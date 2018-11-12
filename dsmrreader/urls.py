from django.conf.urls import include
from django.urls.conf import path
from django.contrib import admin
from django.conf import settings
from rest_framework.documentation import include_docs_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('dsmr_api.urls.v1')),
    path('api/v2/', include('dsmr_api.urls.v2')),
    path('docs/v2/', include_docs_urls(
        title='DSMR-reader API v2',
        description='https://dsmr-reader.readthedocs.io/en/latest/api.html',
        authentication_classes=[],
        permission_classes=[]
    )),
    path('', include('dsmr_frontend.urls')),
]

if settings.DEBUG:
    import debug_toolbar  # pragma: no cover

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]  # pragma: no cover
