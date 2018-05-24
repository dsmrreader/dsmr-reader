from django.contrib import admin
from django.contrib.auth.models import Group, User


# Too bad there is no global admin.py, so we'll just disabled Group & User here.
admin.site.unregister(Group)
admin.site.unregister(User)
