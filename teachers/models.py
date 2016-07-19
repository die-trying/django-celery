from datetime import datetime, timedelta

import iso8601
from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Teacher(models.Model):
    """
    Teacher model

    Represents options, specific to a teacher. Usualy accessable via `user.teacher_data`

    Acceptable lessons
    ==================

    Before teacher can host an event, he should be allowed to do that by adding
    event type to the `acceptable_lessons` property.
    """
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='teacher_data', limit_choices_to={'is_staff': 1})

    acceptable_lessons = models.ManyToManyField(ContentType, related_name='+', limit_choices_to={'app_label': 'lessons'})

    def __str__(self):
        return '%s (%s)' % (self.user.crm.full_name, self.user.username)

    def find_free_slots(self, date, period=timedelta(minutes=30)):
        """
        Get datetime.datetime objects for free slots for a date

        Returns an array of available slots in format ['15:00', '15:30', '16:00']
        """
        hours = WorkingHours.for_date(teacher=self, date=date)
        if hours is None:
            return None

        slots = []
        slot = hours.start
        while slot + period <= hours.end:
            if not self.__check_overlap(slot, period):
                slots.append(slot)
            slot += period
        return slots

    def __check_overlap(self, start, period):
        """
        Check, if a slot does not overlap with other timeline entries

        This implementtion could be less expensive: it creates a timeline entry
        per every testing slot
        """
        TimelineEntry = apps.get_model('timeline.Entry')
        entry = TimelineEntry(
            teacher=self,
            start=start,
            end=start + period,
        )
        return entry.is_overlapping()


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
