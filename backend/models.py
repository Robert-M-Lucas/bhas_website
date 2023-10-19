from django.db import models
from django.conf import settings


class Event(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    deleted = models.BooleanField(default=False)


class Zone(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    title = models.CharField(max_length=50)
    is_circle = models.BooleanField()
    points_or_radius = models.TextField()
