from django.conf.urls import include
from django.urls.conf import path
from django.contrib import admin
from django.conf import settings
from rest_framework.documentation import include_docs_urls
from rest_framework.authentication import TokenAuthentication

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('dsmr_api.urls.v1')),
    path('api/v2/docs/', include_docs_urls(
        title='DSMR-reader API v2',
        description='Docs webbrowser authentication: "Token", Scheme: "Token", Token: "<your API key>"',
        authentication_classes=[TokenAuthentication],
        permission_classes=[]
    )),
    path('api/v2/', include('dsmr_api.urls.v2')),
    path('', include('dsmr_frontend.urls')),
]

if settings.DEBUG:
    import debug_toolbar  # pragma: no cover

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]  # pragma: no cover
