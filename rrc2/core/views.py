from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import SmartDevice, UserDeviceMapping
from .serializers import SmartDeviceSerializer, UserDeviceMappingSerializer


def get_device_detail(request, device_id):
    device = get_object_or_404(SmartDevice, id=device_id)
    data = {
        "id": device.id,
        "description": device.description,
        "address": device.address,
        "maximum_hourly_energy_consumption": str(device.maximum_hourly_energy_consumption)
    }
    return JsonResponse(data)


class SmartDeviceAPIView(APIView):

    def get(self, request):
        if request.auth is None:
            raise AuthenticationFailed('No valid token provided')

        user_role = request.auth.payload.get('role', None)

        if user_role not in ['admin', 'client']:
            raise AuthenticationFailed('Unauthorized role')

        smartDevices = SmartDevice.objects.all()
        serializer = SmartDeviceSerializer(smartDevices, many=True)
        return Response(serializer.data)

    def post(self, request):

        if request.auth is None:
            raise AuthenticationFailed('No valid token provided')

        user_role = request.auth.payload.get('role', None)

        if user_role not in ['admin']:
            raise AuthenticationFailed('Unauthorized role')

        serializer = SmartDeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeviceMappingAPIView(APIView):
    def get(self, request):
        mappings = UserDeviceMapping.objects.all()
        serializer = UserDeviceMappingSerializer(mappings, many=True)
        return Response(serializer.data)


class DeviceDetailView(APIView):
    def delete(self, request, device_id):
        try:
            device = SmartDevice.objects.get(pk=device_id)
        except SmartDevice.DoesNotExist:
            return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateDeviceView(APIView):
    def put(self, request, device_id):

        if request.auth is None:
            raise AuthenticationFailed('No valid token provided')

        user_role = request.auth.payload.get('role', None)

        if user_role not in ['admin']:
            raise AuthenticationFailed('Unauthorized role')

        try:
            device = SmartDevice.objects.get(pk=device_id)
        except SmartDevice.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SmartDeviceSerializer(instance=device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Device updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDevicesView(APIView):
    def get(self, request, user_id):

        if request.auth is None:
            raise AuthenticationFailed('No valid token provided')

        user_role = request.auth.payload.get('role', None)

        if user_role not in ['client']:
            raise AuthenticationFailed('Unauthorized role')

        try:
            user_devices = UserDeviceMapping.objects.filter(user=user_id)
            device_ids = [user_device.device_id for user_device in user_devices]
            device_ids = [device_id for device_id in device_ids if isinstance(device_id, int)]
            devices = SmartDevice.objects.filter(id__in=device_ids)
            serializer = SmartDeviceSerializer(devices, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceIdsView(APIView):
    def get(self, request, *args, **kwargs):
        existing_device_ids = SmartDevice.objects.values_list('id', flat=True)
        existing_device_ids = list(existing_device_ids)
        return JsonResponse(existing_device_ids, safe=False)


class DeviceChangesView(APIView):
    def get(self, request):
        new_devices = SmartDevice.objects.filter(is_active=True).values('device_id')
        deleted_devices = SmartDevice.objects.filter(is_active=False).values('device_id')

        device_changes = [
                             {"action": "add", "device_id": device['device_id']} for device in new_devices
                         ] + [
                             {"action": "delete", "device_id": device['device_id']} for device in deleted_devices
                         ]
        return Response(device_changes)
