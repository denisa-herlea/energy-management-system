from django.urls import path

from . import views
from .views import SmartDeviceAPIView, UpdateDeviceView, UserDevicesView, DeviceIdsView, DeviceChangesView

urlpatterns = [
    path('', SmartDeviceAPIView.as_view()),
    path('smartdevices', SmartDeviceAPIView.as_view()),
    path('smartdevices/delete/<int:device_id>/', views.DeviceDetailView.as_view(), name='device-detail'),
    path('smartdevices/<int:device_id>/', views.get_device_detail, name='device-detail'),
    path('smartdevices/update/<int:device_id>/', UpdateDeviceView.as_view(), name='update-device'),
    path('userdevices/<int:user_id>/', UserDevicesView.as_view(), name='user-devices'),
    path('smartdevices/get_device_ids/', DeviceIdsView.as_view(), name='get_device_ids'),
    path('smartdevices/get_device_changes/', DeviceChangesView.as_view(), name='get_device_changes'),
]