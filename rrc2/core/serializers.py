from rest_framework import serializers
from .models import SmartDevice, UserDeviceMapping


class SmartDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartDevice
        fields = '__all__'


class UserDeviceMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDeviceMapping
        fields = '__all__'
