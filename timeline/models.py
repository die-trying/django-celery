from datetime import timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import capfirst
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.translation import ugettext as _

from accounting.models import Event as AccEvent
from mailer.ical import Ical
from market.auto_schedule import AutoSchedule
from teachers.models import Absence
from timeline.exceptions import DoesNotFitWorkingHours


CLASS_IS_FINISHED_AFTER = timedelta(minutes=60)


class EntryManager(models.Manager):

    def get_queryset(self, exclude_void=True):
        return super(EntryManager, self).get_queryset().exclude(active=0)

    def to_be_marked_as_finished(self):
        """
        Queryset for entries, that are unfinished, and should be automaticaly
        marked as finished.
        """
        return self.get_queryset() \
            .filter(is_finished=False) \
            .filter(end__lte=self.__now() - CLASS_IS_FINISHED_AFTER)

    def by_lesson(self, lesson):
        return self.get_queryset() \
            .filter(lesson_id=lesson.id) \
            .filter(lesson_type=lesson.get_contenttype())

    def __now(self):
        return timezone.now()


class Entry(models.Model):
    """
    timeline.models.Entry

    Single timeline entry
    =====================

    Used for planning teachers time, and for scheduled purchased
    classes (:model:`market.Class`).

    Please import it like this::
        from timeline.models import Entry as TimelineEntry

    Overlapping entries
    ===================

    By default timeline entries can overlap each other. You should set
    instance.`allow_overlap` property to True if you want to enable overlap
    protection.

    You can check overlapping with the `instance.is_overlapping()` method. Checks will be
    done automaticaly, when save() is invoced and allow_overlap == False

    Self-deleting
    =============
    If the entry has no taken slots and is attached to a lesson,
    that does not require a timeline entry — the entry is unused
    and should be deleted.

    This behaviour is needed to free a teacher timeline slot when
    the last student (often — the single), does cancel the class, that
    does not require a by-hand planning, i.e. ordinary lesson.

    You dont need to save an entry
    ==============================
    This model should not incapsulate any scheduling logic. By 'scheduling'
    i meen a process when particular student registers to a planned event from
    timeline or to a generated automaticaly slot.

    Low-level scheduling logic is incapsulated in :model:`market.Class`, and the
    high-level is the `SortingHat` class. This class's concerns should be about
    teacher working hours, timeline representation, counting spare student slots etc.

    So, the prefered situation is when entry is saved by the corresponding
    class, and not by you!

    Timeline entry validation
    =========================
    This model is also used to validate a distinct point in the timetable. The common
    way to validate is to create an entry and run the model clean() method. All checks
    are configurable by boolean instance parameters:
        * allow_besides_working_hours: allow entries the don't fit teachers :model:`teachers.WorkingHours`

    By default all this checks are disabled, you should enable them manualy when creating a model:
    ::
        TimelineEntry = apps.get_model('timeline.Entry')
        entry = TimelineEntry(
            teacher=self,
            start=start,
            end=start + period,
            allow_besides_working_hours=False,
        )
        try:
            entry.clean()
        except ValidationError:
            print "Entry does not fit the timeline!"
        else:
            print "Entry fits the timeline"

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

    teacher = models.ForeignKey('teachers.Teacher', related_name='timeline_entries', on_delete=models.PROTECT)

    start = models.DateTimeField()
    end = models.DateTimeField()

    allow_besides_working_hours = models.BooleanField(default=True)

    lesson_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'app_label': 'lessons'})
    lesson_id = models.PositiveIntegerField(null=True, blank=True)
    lesson = GenericForeignKey('lesson_type', 'lesson_id')

    slots = models.SmallIntegerField('Student slots', default=1)
    taken_slots = models.SmallIntegerField('Students', default=0)

    # TODO — disable assigning of purchased classes to inactive entries
    active = models.SmallIntegerField(choices=ENABLED, default=1)

    is_finished = models.BooleanField(default=False)

    @property
    def is_free(self):
        return self.taken_slots < self.slots

    def get_absolute_url(self):
        return reverse('timeline:entry_card', kwargs={
            'username': self.teacher.user.username,
            'pk': self.pk
        })

    class Meta:
        verbose_name = 'Planned class'
        verbose_name_plural = 'Planned classes'
        permissions = (
            ('other_entries', "Can work with other's timeleine entries"),
        )

    def __str__(self):
        if not self.lesson:
            return _('Usual lesson')

        s = ''

        if self.lesson.slots == 1 and self.classes.count():
            s += "%s: %s" % (self.classes.first().customer.full_name, self.lesson.type_verbose_name)

        else:
            s += '%s (%d/%d)' % (self.lesson.name, self.taken_slots, self.slots)

        return s

    def event_title(self, for_whom='customer'):
        """
        Short event title
        Like 'Signle lesson with Fedor' or 'Defining happyness with Marry'
        """
        lesson_type = capfirst(self.lesson.type_verbose_name)
        lesson_name = self.lesson.name
        teacher = self.teacher.user.crm.first_name

        if for_whom == 'customer':
            if hasattr(self.lesson, 'host'):
                return "{lesson_name} with {teacher}".format(
                    lesson_name=lesson_name,
                    teacher=teacher,
                )
            else:
                return '{lesson_type} with {teacher}'.format(
                    lesson_type=lesson_type,
                    teacher=teacher,
                )

        if for_whom == 'teacher':
            customer = self.classes.first().customer.user.crm.full_name

            if hasattr(self.lesson, 'host'):
                return lesson_name
            else:
                return '{lesson_type} with {customer}'.format(
                    lesson_type=lesson_type,
                    customer=customer,
                )

    def save(self, *args, **kwargs):
        self.__get_data_from_lesson()  # update some data (i.e. available slots) from an assigned lesson
        self.__update_slots()  # update free slot count, check if no classes were added without spare slots for it

        self.__notify_class_that_it_has_been_finished(*args, **kwargs)  # notify a parent class, that it is used and finished
        should_be_deleted = self.__self_delete_if_needed()  # timeline entry should delete itself, if it is not required

        if not should_be_deleted:
            super().save(*args, **kwargs)
        else:
            self.delete()

    def delete(self, src='teacher'):
        """
        Unschedule all attached classes before deletion. Unscheduling a class
        sets it free — user can plan a new lesson on it.
        """
        for c in self.classes.all():
            c.cancel(src)
            c.save()

        for event in AccEvent.objects.by_originator(self):
            event.delete()

        if self.pk:  # if the entry has not autodeleted
            super().delete()

    def is_overlapping(self):
        """
        Check if timeline entry overlapes other entries of the same teacher.
        """
        if self.lesson:
            self.__get_data_from_lesson()   # When the entry is not saved, we can run into situation when we know the lesson, but don't know the end of entry.
        concurent_entries = Entry.objects.filter(end__gt=self.start,
                                                 start__lt=self.end,
                                                 teacher=self.teacher,
                                                 ).exclude(pk=self.pk)

        if concurent_entries.count():
            return True
        return False

    def is_fitting_working_hours(self):
        """
        Check if timeline entry is within its teachers working hours.
        """
        if self.lesson:
            self.__get_data_from_lesson()   # When the entry is not saved, we can run into situation when we know the lesson, but don't know the end of entry.

        hours_start = self.teacher.working_hours.for_date(date=self.start)
        hours_end = self.teacher.working_hours.for_date(date=self.end)

        if hours_start is None or hours_end is None:
            return False

        if not hours_start.does_fit(self.start) or not hours_end.does_fit(self.end):
            return False

        return True

    def teacher_is_present(self):
        """
        Check if teacher has no vacations for the entry period
        """
        if Absence.objects.approved().filter(teacher=self.teacher, start__lt=self.end, end__gt=self.start):
            return False

        return True

    def is_in_past(self):
        """
        Check, if timeline entry is in past
        """
        if self.end < (timezone.now() + CLASS_IS_FINISHED_AFTER):
            return True
        return False

    def as_dict(self):
        """
        Dictionary representation of a model. For details see model description.
        """
        start = timezone.localtime(self.start)
        end = timezone.localtime(self.end)
        return {
            'id': self.pk,
            'title': self.__str__(),
            'start': format(start, 'c'),   # ISO 8601
            'end': format(end, 'c'),       # ISO 8601
            'is_free': self.is_free,
            'slots_taken': self.taken_slots,
            'slots_available': self.slots,
        }

    def as_ical(self, for_whom='customer'):
        ical = Ical(
            start=self.start,
            end=self.end,
            uid=self.pk,
            summary=self.event_title(for_whom),
        )
        return ical.as_string()


    def clean(self):  # NOQA
        """
        TODO: merge it with market.AutoSchedule
        """

        self.__get_data_from_lesson()  # update some data (i.e. available slots) from an assigned lesson

        auto_schedule = AutoSchedule(self.teacher, exclude_timeline_entries=[self.pk])
        auto_schedule.clean(self.start, self.end)

        if not self.allow_besides_working_hours and not self.is_fitting_working_hours():
            raise DoesNotFitWorkingHours('Entry does not fit teachers working hours')

    def __self_delete_if_needed(self):
        """
        If the entry has no taken slots and is attached to a lesson,
        that does not require a timeline entry — the entry is unused
        and should be deleted.

        This behaviour is needed to free a teacher slot when the last
        student (often — the single), does cancel the class, that
        does not require a by-hand planning, i.e. ordinary lesson.
        """
        if not self.pk:
            return False

        if self.taken_slots > 0:
            return False

        if self.lesson and not self.lesson.get_contenttype().model_class().timeline_entry_required():
            return True

        return False

    def __get_data_from_lesson(self):
        """
        Timelentry entry can get some attributes (i.e. available student slots)
        only when it has an assigned lesson.
        """
        if not self.lesson:
            return

        self.slots = self.lesson.slots
        self.end = self.start + self.lesson.duration

        if hasattr(self.lesson, 'host') and self.lesson.host is not None:
            if self.teacher != self.lesson.host:
                raise ValidationError('Trying to assign a timeline entry of %s to %s' % (self.teacher, self.lesson.host))

    def __update_slots(self):
        """
        Count assigned classes and update available time slots.

        If there is too much customers — raise an exception
        """
        if not self.pk:
            return

        self.taken_slots = self.classes.count()

        if self.taken_slots > self.slots:
            raise ValidationError('Trying to assign a class to event without free slots')

    def __notify_class_that_it_has_been_finished(self, *args, **kwargs):
        """
        Mark classes as used, when timeline entry is finished
        """
        if not self.is_finished:
            return
        for c in self.classes.all():
            if not c.is_fully_used:
                c.mark_as_fully_used()
