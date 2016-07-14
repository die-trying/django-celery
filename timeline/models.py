from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.utils.dateformat import format
from django.utils.translation import ugettext as _

from crm.models import Customer


# Create your models here.


class EntryQuerySet(models.QuerySet):
    def free(self):
        """
        Find free timeline entries.
        EDITING THIS YOU SHOULD ALS EDIT Entry.is_free() METHOD!!11
        """
        return self.filter(taken_slots__lte=F('slots'))


class Entry(models.Model):
    """
    A timeline entry

    Used for planning teachers time, and for scheduled bought
    classes (:model:`hub.Class`).

    JSON representation:

    :teacher:
        * id
        * username
    :entry:
        * id — primary key
        * start — start time, ISO 8601
        * end — end time, ISO 8601
        * is_free — Boolean
        * slots_taken — Integer
        * slots_available — Integer
    """
    objects = EntryQuerySet.as_manager()

    teacher = models.ForeignKey(User, related_name='timeline_entries', on_delete=models.PROTECT, limit_choices_to={'is_staff': 1})

    customers = models.ManyToManyField(Customer, related_name='planned_timeline_entries', blank=True)

    start_time = models.DateTimeField()

    lesson_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'app_label': 'lessons'})
    lesson_id = models.PositiveIntegerField(null=True, blank=True)
    lesson = GenericForeignKey('lesson_type', 'lesson_id')

    slots = models.SmallIntegerField(default=1)
    taken_slots = models.SmallIntegerField(default=0)
    duration = models.DurationField(default=timedelta(minutes=30))

    @property
    def is_free(self):
        return self.taken_slots < self.slots

    class Meta:
        verbose_name_plural = 'Entries'
        permissions = (
            ('other_entries', "Can work with other's timeleine entries"),
        )

    def __str__(self):
        if self.lesson:
            return str(self.lesson.name)

        return _('Usual lesson')

    def save(self, *args, **kwargs):
        if self.lesson:
            self.__get_data_from_lesson()  # update some data (i.e. available slots) from an assigned lesson

        if self.pk:
            self.__update_slots()  # update free slot count, check if no customers added when no slots are free

        super().save(*args, **kwargs)

    def as_dict(self):
        """
        Dictionary representation of a model. For details see model description.
        """
        return {
            'id': self.pk,
            'title': self.__str__(),
            'start': format(self.start_time, 'c'),                  # ISO 8601
            'end': format(self.start_time + self.duration, 'c'),    # ISO 8601
            'is_free': self.is_free,
            'slots_taken': self.taken_slots,
            'slots_available': self.slots,
        }

    def __get_data_from_lesson(self):
        """
        Timelentry entry can get some attributes (i.e. available student slote)
        only when it has an assigned lesson.
        """
        self.slots = self.lesson.slots
        self.duration = self.lesson.duration

        if hasattr(self.lesson, 'host') and self.lesson.host is not None:
            if self.teacher != self.lesson.host:
                raise ValidationError('Trying to assign a timeline entry of %s to %s' % (self.teacher, self.lesson.host))

    def __update_slots(self):
        """
        Count assigned customers and update available time slots.

        If there is too much customers — raise an exception
        """
        self.taken_slots = self.customers.count()

        if self.taken_slots > self.slots:
            raise ValidationError('Trying to assign a customer to event without free slots')
