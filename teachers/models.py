from datetime import datetime, timedelta

from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.dateparse import parse_date
from django.utils.translation import ugettext_lazy as _
from django_markdown.models import MarkdownField

from elk.utils.date import day_range


class SlotsList(list):
    def as_dict(self):
        return [i.strftime('%H:%M') for i in self]


class TeacherManager(models.Manager):
    def find_free(self, date, **kwargs):
        """
        Find teachers, that can host a specific event or work with no assigned
        events (by working hours). Accepts kwargs for filtering output of
        :model:`timeline.Entry`.

        Returns an iterable of teachers with assigned attribute free_slots — 
        iterable of available slots as datetime.
        """
        teachers = []
        for teacher in self.get_queryset().all():
            free_slots = teacher.find_free_slots(date, **kwargs)
            if free_slots:
                teacher.free_slots = free_slots
                teachers.append(teacher)
        return teachers


class Teacher(models.Model):
    """
    Teacher model

    Represents options, specific to a teacher. Usualy accessable via `user.teacher_data`

    Acceptable lessons
    ==================

    Before teacher can host an event, he should be allowed to do that by adding
    event type to the `acceptable_lessons` property.
    """
    objects = TeacherManager()
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='teacher_data', limit_choices_to={'is_staff': 1})

    acceptable_lessons = models.ManyToManyField(ContentType, related_name='+', limit_choices_to={'app_label': 'lessons'})

    description = MarkdownField()
    announce = MarkdownField('Short description')

    def as_dict(self):
        return {
            'id': self.pk,
            'name': str(self.user.crm),
            'announce': self.announce,
            'description': self.description,
            'profile_photo': self.user.crm.get_profile_photo(),
        }

    def __str__(self):
        return '%s (%s)' % (self.user.crm.full_name, self.user.username)

    def find_free_slots(self, date, period=timedelta(minutes=30), **kwargs):
        """
        Get datetime.datetime objects for free slots for a date. Accepts kwargs
        for filtering output of :model:`timeline.Entry`.

        Returns an iterable of available slots in format ['15:00', '15:30', '16:00']
        """
        self.__check_if_lesson_requires_timeline_entry(kwargs)

        # if the only kwarg was lesson_type and previous method had deleted it,
        # we'll return all available time for the teacher
        if len(kwargs.keys()):
            return self.__find_timeline_entries(date=date, **kwargs)

        hours = WorkingHours.objects.for_date(teacher=self, date=date)
        if hours is None:
            return None
        return self.__all_free_slots(hours.start, hours.end, period)

    def __find_timeline_entries(self, date, **kwargs):
        """
        Find timeline entries of lessons with specific type, assigned to current
        teachers. Accepts kwargs for filtering output of :model:`timeline.Entry`.

        Returns an iterable of slots as datetime objects.
        """
        TimelineEntry = apps.get_model('timeline.entry')

        slots = SlotsList()
        for entry in TimelineEntry.objects.filter(teacher=self, start__range=day_range(date), **kwargs):
            slots.append(entry.start)
        return slots

    def __all_free_slots(self, start, end, period):
        """
        Get all existing time slots, not checking an event type — by teacher's
        working hours.

        Returns an iterable of slots as datetime objects.
        """
        slots = SlotsList()
        slot = start
        while slot + period <= end:
            if not self.__check_overlap(slot, period):
                if slot >= self.__today():
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

    def __check_if_lesson_requires_timeline_entry(self, kwargs):
        """
        Check if lesson class, passed as filter to free_slots() requires a timeline
        slot. If not — delete this filter argument from kwargs.
        """
        lesson_type = kwargs.get('lesson_type')
        if lesson_type is None:
            return

        try:
            Lesson_model = ContentType.objects.get(pk=lesson_type).model_class()
        except ContentType.DoesNotExist:
            return

        if not Lesson_model.timeline_entry_required():
            del kwargs['lesson_type']

    def __today(self):
        return datetime.now()


class WorkingHoursManager(models.Manager):
    def for_date(self, date, teacher):
        """
        Returns an iterable of date objects for start of working time and end of
        working time for the distinct date.
        """
        date = parse_date(date)
        try:
            hours = self.get(teacher=teacher, weekday=date.weekday())
        except ObjectDoesNotExist:
            return None
        else:
            hours.start = datetime.combine(date, hours.start)
            hours.end = datetime.combine(date, hours.end)
            return hours


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
    objects = WorkingHoursManager()
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

    def does_fit(self, time):
        """
        Check if time fits within working hours
        """
        if time >= self.start and time <= self.end:
            return True
        return False

    def __str__(self):
        return '%s: day %d %s—%s' % (self.teacher.user.username, self.weekday, self.start, self.end)

    class Meta:
        unique_together = ('teacher', 'weekday')
        verbose_name_plural = "Working hours"
