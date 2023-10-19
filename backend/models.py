from dataclasses import dataclass

from django.db import models
from django.conf import settings


@dataclass
class Position:
    latitude: float
    longitude: float

    @staticmethod
    def from_string(string):
        pos = [float(x) for x in string.split(',')]
        return Position(pos[0], pos[1])

    def to_string(self):
        if abs(self.longitude) > 200 or abs(self.latitude) > 200:
            raise ValueError

        return f'{round(self.latitude, 10)},{round(self.longitude, 10)}'

    def as_json(self):
        return f'{{"latitude":{self.latitude},"longitude":{self.latitude}}}'


class Event(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    center = models.CharField(max_length=40)
    deleted = models.BooleanField(default=False)


class Zone(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    title = models.CharField(max_length=50)
    index = models.IntegerField()
    is_circle = models.BooleanField()
    points_or_center = models.TextField()
    hole_points_or_radius = models.TextField()
    deleted = models.BooleanField(default=False)


class SocietyMessage(models.Model):
    id = models.BigAutoField(primary_key=True)
    message = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    @staticmethod
    def get_message():
        try:
            return SocietyMessage.objects.get(deleted=False).message
        except SocietyMessage.DoesNotExist:
            SocietyMessage.objects.create(message="Welcome to Bath Hide and Seek")
            return "Welcome to Bath Hide and Seek"

    @staticmethod
    def set_message(message):
        for message_obj in SocietyMessage.objects.filter(deleted=False):
            message_obj.deleted = True
            message_obj.save()

        SocietyMessage.objects.create(message=message)
