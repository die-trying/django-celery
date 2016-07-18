from datetime import datetime, timedelta

import iso8601
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Teacher(models.Model):
    """
    Teacher model

    Represent options, specific to a teacher.
    Usualy accessable via `user.teacher_data`
    """
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='teacher_data', limit_choices_to={'is_staff': 1})

    def __str__(self):
        return '%s (%s)' % (self.user.crm.full_name, self.user.username)

    def find_free_slots(self, date, period=timedelta(minutes=30)):
        """
        Get datetime.datetime objects for free slots for a date
        """
        hours = WorkingHours.for_date(teacher=self, date=date)
        if hours is None:
            return None

        slots = []
        slot = hours.start
        while slot + period <= hours.end:
            slots.append(slot)
            slot += period
        return slots


class WorkingHours(models.Model):
    WEEKDAYS = (
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    )
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='working_hours')

    weekday = models.IntegerField('Weekday', choices=WEEKDAYS)
    start = models.TimeField('Start hour (UTC)')
    end = models.TimeField('End hoour(UTC)')

    def as_dict(self):
        return {
            'id': self.pk,
            'weekday': self.weekday,
            'start': str(self.start),
            'end': str(self.end)
        }

    @classmethod
    def for_date(cls, teacher, date):
        """
        Returns date objects for start of working time and end of working time
        for the distinct date
        """
        date = iso8601.parse_date(date)
        try:
            hours = cls.objects.get(teacher=teacher, weekday=date.weekday())
        except cls.DoesNotExist:
            return None
        else:
            hours.start = datetime.combine(date, hours.start)
            hours.end = datetime.combine(date, hours.end)
            return hours

    def __str__(self):
        return '%s: day %d' % (self.teacher.user.username, self.weekday)

    class Meta:
        unique_together = ('teacher', 'weekday')
        verbose_name_plural = "Working hours"
