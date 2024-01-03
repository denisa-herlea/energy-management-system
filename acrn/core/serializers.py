from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = '__all__'
