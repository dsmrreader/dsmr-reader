from rest_framework import serializers

from dsmr_datalogger.models.statistics import MeterStatistics


class MeterStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeterStatistics
        fields = '__all__'
