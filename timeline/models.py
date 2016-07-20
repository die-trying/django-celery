from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.dateformat import format
from django.utils.translation import ugettext as _

from crm.models import Customer
from lessons.models import Lesson
from teachers.models import Teacher

ALLOWED_TIMELINE_FILTERS = ('lesson_type', 'lesson_id')  # list of filters, allowed for ordinary users through get parameters


class EntryManager(models.Manager):

    def get_queryset(self, exclude_void=True):
        return super(EntryManager, self).get_queryset().exclude(active=0)


class Entry(models.Model):
    """
    timeline.models.Entry

    Single timeline entry
    =====================

    Used for planning teachers time, and for scheduled bought
    classes (:model:`hub.Class`).

    Please import it like this::
        from timeline.models import Entry as TimelineEntry

    OVERLAPPING ENTRIES
    ===================

    By default timeline entries can overlap each other. You should set
    instance.`allow_overlap` property to True if you want to enable overlap
    protection.

    You can check overlapping with the `instance.is_overlapping()` method. Checks will be
    done automaticaly, when save() is invoced and allow_overlap == False

    JSON representation
    ===================

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
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )

    objects = EntryManager()

    teacher = models.ForeignKey(Teacher, related_name='timeline_entries', on_delete=models.PROTECT)

    customers = models.ManyToManyField(Customer, related_name='planned_timeline_entries', blank=True)

    start = models.DateTimeField()
    end = models.DateTimeField()
    allow_overlap = models.BooleanField(default=True)

    lesson_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'app_label': 'lessons'})
    lesson_id = models.PositiveIntegerField(null=True, blank=True)
    lesson = GenericForeignKey('lesson_type', 'lesson_id')
    lessons = GenericRelation(Lesson, related_query_name='timeline_entries')

    slots = models.SmallIntegerField(default=1)
    taken_slots = models.SmallIntegerField(default=0)

    # TODO — disable assigning of bought classes to inactive entries
    active = models.SmallIntegerField(choices=ENABLED, default=1)

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

        if not self.allow_overlap and self.is_overlapping():
            raise ValidationError('Entry time overlapes with some other entry of this teacher')

        if self.pk:
            self.__update_slots()  # update free slot count, check if no customers added when no slots are free

        super().save(*args, **kwargs)

    def is_overlapping(self):
        """
        Check if timeline entry overlapes other entries of the same teacher.
        """
        concurent_entries = Entry.objects.filter(end__gt=self.start,
                                                 start__lt=self.end,
                                                 teacher=self.teacher
                                                 )
        if concurent_entries.count():
            return True
        return False

    def as_dict(self):
        """
        Dictionary representation of a model. For details see model description.
        """
        return {
            'id': self.pk,
            'title': self.__str__(),
            'start': format(self.start, 'c'),   # ISO 8601
            'end': format(self.end, 'c'),       # ISO 8601
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
        self.end = self.start + self.lesson.duration

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
