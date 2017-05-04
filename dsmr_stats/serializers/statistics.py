from rest_framework import serializers

from dsmr_stats.models.statistics import DayStatistics, HourStatistics


class DayStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayStatistics
        fields = '__all__'


class HourStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourStatistics
        fields = '__all__'
