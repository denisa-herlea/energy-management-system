from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Measurement
from .serializers import *


# Create your views here.
class MeasurementViewset(viewsets.ViewSet):
    def list(self, request):
        measurements = Measurement.objects.all()
        serializer = MeasurementSerializer(measurements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    """
    def create(self, request):
        serializer = MeasurementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        product = Measurement.objects.get(pk=pk)
        serializer = MeasurementSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        measurement = Measurement.objects.get(pk=pk)
        serializer = MeasurementSerializer(instance=measurement, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        measurement = Measurement.objects.get(pk=pk)
        measurement.delete()

        return Response('Measurement deleted')
    """