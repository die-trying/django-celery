from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

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
    objects = EntryQuerySet.as_manager()

    teacher = models.ForeignKey(User, related_name='timeline_entries', on_delete=models.PROTECT, limit_choices_to={'is_staff': 1})

    customers = models.ManyToManyField(Customer, related_name='planned_timeline_entries', blank=True)

    start_time = models.DateTimeField()

    event_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'app_label': 'lessons'})
    event_id = models.PositiveIntegerField(null=True, blank=True)
    event = GenericForeignKey('event_type', 'event_id')

    slots = models.SmallIntegerField(default=1)
    taken_slots = models.SmallIntegerField(default=0)

    @property
    def is_free(self):
        return self.taken_slots < self.slots

    class Meta:
        verbose_name_plural = 'Entries'

    def __str__(self):
        if self.event:
            return '%s: %s' % (self.teacher.crm.full_name, self.event)

        start_time = self.start_time
        return '%s scheduled on %s' % (self.teacher.crm.full_name, start_time.strftime('%d.%m.%Y %H:%M'))

    def save(self, *args, **kwargs):
        if self.event:
            self.slots = self.event.slots  # The next change in this method should refactor it!

            if self.teacher != self.event.host:
                raise ValidationError('Trying to assign a timeline entry of %s to %s' % (self.teacher, self.event.host))

        if self.pk:
            self.taken_slots = self.customers.count()

        if self.taken_slots > self.slots:
            raise ValidationError('Trying to assign a customer to a non-free event')

        super().save(*args, **kwargs)
