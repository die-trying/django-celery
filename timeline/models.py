from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError

from crm.models import Customer

# Create your models here.


class EntryQuerySet(models.QuerySet):
    def free(self):
        """
        Find free timeline entries.
        EDITING THIS YOU SHOULD ALS EDIT Entry.is_free() METHOD!!11
        """
        return self.filter(customer=None)


class Entry(models.Model):
    objects = EntryQuerySet.as_manager()

    teacher = models.ForeignKey(User, related_name='timeline_entries', on_delete=models.PROTECT, limit_choices_to={'is_staff': 1})
    customer = models.ForeignKey(Customer, related_name='planned_lessons', on_delete=models.SET_NULL, null=True, blank=True)

    start_time = models.DateTimeField()

    event_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'app_label': 'lessons'})
    event_id = models.PositiveIntegerField(null=True, blank=True)
    event = GenericForeignKey('event_type', 'event_id')

    def __str__(self):
        if self.event:
            return '%s: %s' % (self.teacher.crm.full_name, self.event)

        start_time = self.start_time
        return '%s on %s' % (self.teacher.crm.full_name, start_time.strftime('%d.%m.%Y %H:%M'))

    @property
    def is_free(self):
        if self.customer:
            return False
        return True

    @property
    def duration(self):
        return self._get_event_property('duration')

    @property
    def slots(self):
        return self._get_event_property('slots')

    def assign_event(self, event):
        self.event = event
        self.save()

    class Meta:
        verbose_name_plural = 'Entries'

    def _get_event_property(self, property):
        if not self.event:
            raise FieldError('Entry %s has any assigned event' % self)
        return getattr(self.event, property)
