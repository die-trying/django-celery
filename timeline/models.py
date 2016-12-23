
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import capfirst
from django.utils import timezone
from django.utils.translation import ugettext as _

from accounting.models import Event as AccEvent
from mailer.ical import Ical
from market.auto_schedule import AutoSchedule
from market.exceptions import AutoScheduleExpcetion
from timeline import exceptions


class EntryManager(models.Manager):
    def to_be_marked_as_finished(self):
        """
        Queryset for entries, non-finished timeline entries that should be
        marked as finished.
        """
        return self.get_queryset() \
            .filter(is_finished=False) \
            .filter(end__lte=timezone.now() - settings.CLASS_IS_FINISHED_AFTER)

    def by_lesson(self, lesson):
        return self.get_queryset() \
            .filter(lesson_id=lesson.id) \
            .filter(lesson_type=lesson.get_contenttype())

    def hosted_lessons_starting_soon(self, lesson_types):
        """
        Lessons that are starting soon, filtered by lesson_types.

        Assuming no one will search for non-hosted lessons (all of them are already scheduled one-on-one),
        returns only lessons that have a host.
        """
        entries = self.get_queryset() \
            .filter(lesson_type__in=lesson_types) \
            .filter(start__gte=timezone.now()) \
            .filter(taken_slots__lt=models.F('slots')) \
            .distinct('lesson_type', 'lesson_id')

        for entry in entries:
            if entry.lesson.get_photo() is not None:
                if entry.lesson.host is not None:
                    yield entry.lesson

    def timeslots_by_lesson(self, lesson, start, end):
        """
        Generate timeslots for lesson
        """
        for entry in self.by_lesson(lesson).filter(start__range=(start, end)):
            if entry.is_free:
                try:
                    entry.clean()
                except (AutoScheduleExpcetion, exceptions.DoesNotFitWorkingHours):
                    continue
                yield entry.start

    def lessons_for_date(self, start, end, **kwargs):
        """
        Get all lessons, that have timeline entries for the requested period.

        Ignores timeslot availability
        """
        entries = self.get_queryset() \
            .filter(start__range=(start, end)) \
            .filter(**kwargs) \
            .distinct('lesson_type', 'lesson_id')

        for entry in entries:
            yield entry.lesson


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

    Event titles
    ===================
    There a 2 types of event title — for customer and for the teacher.

    Event title for the customer is generated by event_title() method.
    Event title for the teacher is generated by django str representation of an instance.
    """
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
        """
        Event title for the teacher

        Be carefull with SQL queries in this method, it is called for
        every single timeline entry and can cause a heavy load when
        looking into the teachers timeline.
        """
        customers = self.classes.values_list('customer__user__first_name', 'customer__user__last_name')

        if hasattr(self.lesson, 'host'):  # return lesson name if lesson is hosted
            title = str(self.lesson)
            if len(customers):  # append customer count if someone already has registered
                title += ' {}/{}'.format(self.taken_slots, self.slots)
            return title

        if len(customers):
            return ' '.join(customers[0])

        return _('Usual lesson')

    def event_title(self):
        """
        Short event title for the customer
        Like 'Signle lesson with Fedor' or 'Defining happyness with Mary'
        """
        teacher = self.teacher.user.crm.first_name

        if hasattr(self.lesson, 'host'):
            return "«{lesson_name}» with {teacher}".format(
                lesson_name=self.lesson.name,
                teacher=teacher,
            )
        else:
            return '{lesson_type} with {teacher}'.format(
                lesson_type=capfirst(self.lesson.type_verbose_name),
                teacher=teacher
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

    def has_started(self):
        """
        Did entry start
        """
        return self.start <= timezone.now()

    def has_finished(self):
        """
        Check, if timeline entry is in past
        """
        if self.end < (timezone.now() + settings.CLASS_IS_FINISHED_AFTER):
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

    def as_ical(self, for_whom='customer'):
        if for_whom == 'customer':
            title = self.event_title()
        else:  # for the teacher
            title = str(self)

        ical = Ical(
            start=self.start,
            end=self.end,
            uid=self.pk,
            summary=title,
        )
        return ical.as_string()

    def clean(self):
        self.__get_data_from_lesson()  # update some data (i.e. available slots) from an assigned lesson

        if self.taken_slots >= 1:  # there is no need to validate timeline entries when they have students
            return

        auto_schedule = AutoSchedule(self.teacher, exclude_timeline_entries=[self.pk])
        auto_schedule.clean(self.start, self.end)

        if not self.allow_besides_working_hours and not self.is_fitting_working_hours():
            raise exceptions.DoesNotFitWorkingHours('Entry does not fit teachers working hours')

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
