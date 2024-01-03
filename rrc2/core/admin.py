from django.contrib import admin

from .models import SmartDevice, UserDeviceMapping


@admin.register(SmartDevice)
class SmartDeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'address', 'maximum_hourly_energy_consumption']


@admin.register(UserDeviceMapping)
class UserDeviceMappingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'device']
