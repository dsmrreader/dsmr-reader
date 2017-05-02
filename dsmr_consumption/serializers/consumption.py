from rest_framework import serializers

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption


class ElectricityConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectricityConsumption
        fields = '__all__'


class GasConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasConsumption
        fields = '__all__'
