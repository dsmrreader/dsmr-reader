from django.urls.conf import path

from dsmr_dropbox.views import DropboxAppAuthorizationView


app_name = "dropbox"

urlpatterns = [
    path("app/authorize", DropboxAppAuthorizationView.as_view(), name="authorize-app"),
]
