from rest_framework import serializers

from dsmr_consumption.models.consumption import (
    ElectricityConsumption,
    GasConsumption,
    QuarterHourPeakElectricityConsumption,
)
from dsmr_consumption.models.energysupplier import EnergySupplierPrice


class EnergySupplierPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergySupplierPrice
        fields = "__all__"


class ElectricityConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectricityConsumption
        fields = "__all__"


class QuarterHourPeakElectricityConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuarterHourPeakElectricityConsumption
        fields = "__all__"


class GasConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasConsumption
        fields = "__all__"
