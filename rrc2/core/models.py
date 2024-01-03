from django.db import models


class SmartDevice(models.Model):
    id = models.AutoField(primary_key=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    maximum_hourly_energy_consumption = models.DecimalField(max_digits=10, decimal_places=2)


class UserDeviceMapping(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.IntegerField()
    device = models.ForeignKey(SmartDevice, on_delete=models.CASCADE)
