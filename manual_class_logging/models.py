from django.db import models

from market.models import Class
from teachers.models import Teacher


class ManualClassLogEntry(models.Model):
    """
    Temporary model to store completed-by-hand classes. We'll remove the whole app
    after final moving from vCita
    """
    teacher = models.ForeignKey(Teacher, related_name='manualy_completed_classes')
    Class = models.ForeignKey(Class, related_name='manualy_completed_classes')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Completed class'
        verbose_name_plural = 'Completed classes'
