from abc import abstractproperty
from datetime import datetime, timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from djmoney.models.fields import MoneyField

from crm.models import Customer
from hub.exceptions import CannotBeScheduled, CannotBeUnscheduled
from timeline.models import Entry as TimelineEntry


class BuyableProduct(models.Model):
    """
    Parent of every buyable object
    """
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )

    buy_time = models.DateTimeField(auto_now_add=True)
    buy_price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    active = models.SmallIntegerField(choices=ENABLED, default=1)

    @abstractproperty
    def name_for_user(self):
        pass

    class Meta:
        abstract = True


class Subscription(BuyableProduct):
    """
    Represents a single bought subscription.

    When buying a subscription, one should store request in the `request`
    property of this instance. This is neeed for the log entry to contain
    request data requeired for futher analysis.

    The property is accessed later in the history.signals module.
    """

    customer = models.ForeignKey(Customer, related_name='subscriptions')

    product_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    product = GenericForeignKey('product_type', 'product_id')

    @property
    def name_for_user(self):
        return self.product.name

    def save(self, *args, **kwargs):
        is_new = True
        if self.pk:
            is_new = False

        if not is_new:  # check, if we should enable\disable lessons
            self.__update_classes()

        super(Subscription, self).save(*args, **kwargs)

        if is_new:
            self.__add_lessons_to_user()

    def __add_lessons_to_user(self):
        """
        When creating new subscription, we should make included lessons
        available for the customer.
        """
        for lesson_type in self.product.LESSONS:
            for lesson in getattr(self.product, lesson_type).all():
                c = Class(
                    lesson=lesson,
                    subscription=self,
                    customer=self.customer,
                    buy_price=self.buy_price,
                    buy_source=1,  # store a sign, that class is bought by subscription
                )
                c.request = self.request  # bypass request object for later analysis
                c.save()

    def __update_classes(self):
        """
        When the subscription is disabled for any reasons, all lessons
        assosciated to it, should be disabled too.
        """
        orig = Subscription.objects.get(pk=self.pk)
        if orig.active != self.active:
            for lesson in self.classes.all():
                lesson.active = self.active
                lesson.save()


class ClassesManager(models.Manager):
    def bought_lesson_types(self):
        """
        Get ContentTypes for lessons, available to user
        """
        types = self.get_queryset().filter(timeline_entry__isnull=True).values_list('lesson_type', flat=True).distinct()
        return ContentType.objects.filter(pk__in=types)

    def dates_for_planning(self):
        """
        A generator of dates, available for planning for particular user

        Currently retures 7 future days for everyone.
        """
        current = datetime.now()
        end = current + timedelta(days=7)

        while current < end:
            yield current
            current += timedelta(days=1)


class Class(BuyableProduct):
    """
    Represents a single bought lesson. When buying a class, one should
    store request in the `request` property of this instance. This is neeed for
    the log entry to contain request data requeired for futher analysis.

    The property is accessed later in the history.signals module.
    """
    BUY_SOURCES = (
        (0, 'Single'),
        (1, 'Subscription')
    )

    objects = ClassesManager()

    customer = models.ForeignKey(Customer, related_name='classes')

    buy_source = models.SmallIntegerField(choices=BUY_SOURCES, default=0)

    lesson_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    lesson_id = models.PositiveIntegerField()
    lesson = GenericForeignKey('lesson_type', 'lesson_id')

    timeline_entry = models.ForeignKey(TimelineEntry, null=True, blank=True, related_name='classes')

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, related_name='classes')

    @property
    def name_for_user(self):
        return self.lesson.name

    def __str__(self):
        if self.subscription:
            return "#%d %s by %s for %s" % (self.pk, self.lesson, self.subscription.product, self.customer)
        return "#%d %s for %s" % (self.pk, self.lesson, self.customer)

    def schedule(self, entry):
        """
        Schedule a lesson — assign a timeline entry.
        """
        if not self.can_be_scheduled(entry):
            raise CannotBeScheduled('%s %s' % (self, entry))

        entry.customers.add(self.customer)
        entry.save()

        self.timeline_entry = entry

    def unschedule(self):
        """
        Unschedule previously scheduled lesson
        """
        if not self.timeline_entry:
            raise CannotBeUnscheduled('%s' % self)

        # TODO — check if entry is not completed
        self.timeline_entry.customers.remove(self.customer)
        self.timeline_entry.save()
        self.timeline_entry = None

    @property
    def is_scheduled(self):
        """
        Check if class is scheduled — has an assigned timeline entry and other
        """
        if self.timeline_entry:
            return True

        return False

    def can_be_scheduled(self, entry):
        """
        Check if timeline entry can be scheduled
        """
        if self.is_scheduled:
            return False

        if not entry.is_free:
            return False

        if self.lesson_type != entry.lesson_type:
            return False

        return True
