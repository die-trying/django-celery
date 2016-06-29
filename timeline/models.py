from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Entry(models.Model):
    teacher = models.ForeignKey(User, related_name='timeline_entries', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_staff': 1})
    customer = models.ForeignKey(User, related_name='planned_lessons', on_delete=models.SET_NULL, null=True, blank=True)

    start_time = models.DateTimeField()
    duration = models.DurationField(default=timedelta(minutes=30))

    slots = models.SmallIntegerField()
