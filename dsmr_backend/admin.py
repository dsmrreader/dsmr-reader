from django.contrib import admin
from django.contrib.auth.models import Group


# Too bad there is no global admin.py, so we'll just disabled Group here.
admin.site.unregister(Group)
