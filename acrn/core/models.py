from django.db import models


class Measurement(models.Model):
    device_id = models.IntegerField()
    hourly_average = models.FloatField()
    start_hour = models.IntegerField(null=True, blank=True)
    end_hour = models.IntegerField(null=True, blank=True)
    measurement_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_id} - {self.hourly_average} - {self.start_hour} - {self.end_hour} "
