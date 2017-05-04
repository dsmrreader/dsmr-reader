from rest_framework import serializers

from dsmr_datalogger.models.reading import DsmrReading


class DsmrReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DsmrReading
        exclude = ('processed', )
