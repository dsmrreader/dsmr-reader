from rest_framework import serializers

from dsmr_backend.models.settings import EmailSettings


class EmailSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSettings
        exclude = ['id']
