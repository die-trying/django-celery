import datetime

import pytz
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.translation import ugettext_lazy as _
from django_markdown.models import MarkdownField
from image_cropping import ImageRatioField
from image_cropping.templatetags.cropping import cropped_thumbnail

from elk.utils.date import day_range, minute_after_midnight, minute_till_midnight
from market.auto_schedule import AutoSchedule
from market.exceptions import AutoScheduleExpcetion
from teachers.slot_list import SlotList
from timeline.exceptions import DoesNotFitWorkingHours

TEACHER_GROUP_ID = 2  # PK of django.contrib.auth.models.Group with the teacher django-admin permissions

PLANNING_DELTA = datetime.timedelta(days=1)  # booking lag


def _planning_ofsset(start):
    """
    Returns a minimal start time, that is available for planning
    """

    if start < (timezone.now() + PLANNING_DELTA):
        start = timezone.now() + PLANNING_DELTA

    if start.minute > 0 and start.minute < 30:
        start = start.replace(minute=30)

    if start.minute > 30:
        start = start + datetime.timedelta(hours=1)
        start = start.replace(minute=0)

    return start


class TeacherManager(models.Manager):
    def with_photos(self):
        return super().get_queryset() \
            .filter(active=1) \
            .exclude(teacher_photo='') \
            .exclude(teacher_photo__isnull=True)

    def find_free(self, date, **kwargs):
        """
        Find teachers, that can host a specific event or work with no assigned
        events (by working hours). Accepts kwargs for filtering output of
        :model:`timeline.Entry`.

        Returns an iterable of teachers with assigned attribute free_slots — 
        iterable of available slots as datetime.
        """
        teachers = []
        for teacher in self.with_photos().filter(active=1):
            free_slots = teacher.find_free_slots(date, **kwargs)
            if free_slots:
                teacher.free_slots = free_slots
                teachers.append(teacher)
        return teachers

    def find_lessons(self, date, **kwargs):
        """
        Find all lessons, that are planned to a date. Accepts keyword agruments
        for filtering output of :model:`timeline.Entry`.

        TODO: refactor this method
        """
        start = _planning_ofsset(date)
        end = start.replace(hour=23, minute=59)

        lessons = []
        for lesson in self.__lessons_for_date(start, end, **kwargs):
            lesson.free_slots = SlotList(self.__timeslots_by_lesson(lesson, start, end))
            if len(lesson.free_slots):
                lessons.append(lesson)

        return lessons

    def __lessons_for_date(self, start, end, **kwargs):
        """
        Get all lessons, that have timeline entries for the requested period.

        Ignores timeslot availability
        """
        TimelineEntry = apps.get_model('timeline.entry')
        for timeline_entry in TimelineEntry.objects.filter(start__range=(start, end)).filter(**kwargs).distinct('lesson_id'):
            yield timeline_entry.lesson

    def __timeslots_by_lesson(self, lesson, start, end):
        """
        Generate timeslots for lesson
        """
        TimelineEntry = apps.get_model('timeline.entry')
        for entry in TimelineEntry.objects.by_lesson(lesson).filter(start__range=(start, end)):
            if entry.is_free:
                yield entry.start

    def can_finish_classes(self):
        """
        TODO: refactor it, admin interface should care about it choices
        """
        return [('-1', 'Choose a teacher')] + [(t.pk, t.user.crm.full_name) for t in self.get_queryset().filter(active=1)]


class Teacher(models.Model):
    """
    Teacher model

    Represents options, specific to a teacher. Usualy accessable via `user.teacher_data`

    Acceptable lessons
    ==================

    Before teacher can host an event, he should be allowed to do that by adding
    event type to the `allowed_lessons` property.
    """
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )
    objects = TeacherManager()
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='teacher_data', limit_choices_to={'is_staff': 1, 'crm__isnull': False})

    allowed_lessons = models.ManyToManyField(ContentType, related_name='+', blank=True, limit_choices_to={'app_label': 'lessons'})

    teacher_photo = models.ImageField(upload_to='teachers/', null=True, blank=True)
    teacher_photo_cropping = ImageRatioField('teacher_photo', '500x500')

    description = MarkdownField()
    announce = models.TextField(max_length=140)
    active = models.IntegerField(default=1, choices=ENABLED)

    class Meta:
        verbose_name = 'Teacher profile'

    def save(self, *args, **kwargs):
        """
        Add new teachers to the 'teachers' group
        """
        if not self.pk:
            try:
                group = Group.objects.get(pk=TEACHER_GROUP_ID)
                self.user.groups.add(group)
                self.user.save()
            except Group.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return '%s (%s)' % (self.user.crm.full_name, self.user.username)

    def get_teacher_photo(self):
        """
        Get, if exists, big teachers photo
        """
        if self.teacher_photo:
            return cropped_thumbnail(context={}, instance=self, ratiofieldname='teacher_photo_cropping')

    def find_free_slots(self, date, period=datetime.timedelta(minutes=30), **kwargs):
        """
        Get datetime.datetime objects for free slots for a date. Accepts keyword
        arguments for filtering output of :model:`timeline.Entry`.

        Returns an iterable of available slots in format ['15:00', '15:30', '16:00']
        """
        self.__delete_lesson_types_that_dont_require_a_timeline_entry(kwargs)

        # if there are any filters left — find timeline entries
        if len(kwargs.keys()):
            return SlotList(self.__find_timeline_entries(date=date, **kwargs))

        # otherwise — return all available time based on working hours
        hours = self.working_hours.for_date(date=date)
        if hours is None:
            return None

        if hours.end > timezone.make_aware(minute_till_midnight(date)):
            hours.end = timezone.make_aware(minute_after_midnight(date))

        auto_schedule = AutoSchedule(teacher=self)
        return auto_schedule.slots(hours.start, hours.end, period)

    def free_slots_for_dates(self, dates):
        """
        Get an iterable of by-day auto schedule
        """
        for date in dates:
            yield {
                'date': date,
                'slots': self.find_free_slots(date)
            }

    def available_lessons(self, lesson_type):
        """
        Get list of lessons, that teacher can lead
        """
        for i in self.allowed_lessons.all():
            if i == lesson_type:
                Model = i.model_class()
                if hasattr(Model, 'host'):
                    return Model.objects.filter(host=self)
                else:
                    return [Model.get_default()]  # all non-hosted lessons except the default one are for subscriptions, nobody needs to host or plan them
        return []

    def available_lesson_types(self):
        """
        Get contenttypes of lessons, allowed to host
        """
        lesson_types = {}
        for i in self.allowed_lessons.all():
            Model = i.model_class()

            if not hasattr(Model, 'sort_order'):
                continue

            if hasattr(Model, 'host') and not self.available_lessons(i):  # hosted lessons should be returned only if they have lessons
                continue

            lesson_types[Model.sort_order()] = i

        for i in sorted(list(lesson_types.keys())):
            yield lesson_types[i]

    def get_absolute_url(self):
        """
        Teacher detail page
        """
        return reverse('teachers:detail', kwargs={'username': self.user.username})

    def timeline_url(self):
        """
        Get teacher's timeline URL
        """
        return reverse('timeline:timeline', kwargs={'username': self.user.username})

    def __find_timeline_entries(self, date, **kwargs):
        """
        Find timeline entries of lessons with specific type, assigned to current
        teachers. Accepts kwargs for filtering output of :model:`timeline.Entry`.

        Returns an iterable of slots as datetime objects.
        """
        TimelineEntry = apps.get_model('timeline.entry')
        for entry in TimelineEntry.objects.filter(teacher=self, start__range=day_range(date), **kwargs):
            if entry.is_free:
                try:
                    entry.clean()
                except (AutoScheduleExpcetion, DoesNotFitWorkingHours) as e:
                    continue

                yield entry.start

    def __delete_lesson_types_that_dont_require_a_timeline_entry(self, kwargs):
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


class WorkingHoursManager(models.Manager):
    def for_date(self, date):
        """
        Return working hours object for the date.

        All working hours objects are returned in the server timezone, defined
        in settings.TIME_ZONE
        """

        date = timezone.localtime(date)

        try:
            hours = self.get(weekday=date.weekday())
        except ObjectDoesNotExist:
            return None

        server_tz = pytz.timezone(settings.TIME_ZONE)

        hours.start = timezone.make_aware(datetime.datetime.combine(date, hours.start), timezone=server_tz)
        hours.end = timezone.make_aware(datetime.datetime.combine(date, hours.end), timezone=server_tz)

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
    start = models.TimeField('Start hour (EDT)')
    end = models.TimeField('End hour (EDT)')

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


class AbsenceManager(models.Manager):
    def approved(self):
        return self.get_queryset().filter(is_approved=True)


class Absence(models.Model):
    ABSENCE_TYPES = (
        ('vacation', _('Vacation')),
        ('unpaid', _('Unpaid')),
        ('sick', _('Sick leave')),
        ('bonus', _('Bonus vacation')),
        ('srv', _('System-intiated vacation'))
    )

    objects = AbsenceManager()

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='absences')
    type = models.CharField(max_length=32, choices=ABSENCE_TYPES, default='srv')
    start = models.DateTimeField('Start')
    end = models.DateTimeField('End')
    add_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return '%s of %s from %s to %s' % \
            (self.type, str(self.teacher), format(self.start, 'Y-m-d H:i'), format(self.end, 'Y-m-d H:i'))
