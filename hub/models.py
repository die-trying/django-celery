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

        ContentType.objects.filter(pk__in=types)

        sort_order = {}
        # Sort found lessons by order, defined in their sort_order() methods.
        # If a lesson does not implement such method, it will be excluded from
        # sort results.
        for t in ContentType.objects.filter(pk__in=types):
            Model = t.model_class()
            order = Model.sort_order()
            if order:
                sort_order[order] = t

        result = []
        for i in sorted(sort_order.keys()):
            result.append(sort_order[i])
        return result

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

    def find_class(self, **kwargs):
        """
        Find a class to schedule. Accept filters :model:`hub.Class` queryset.
        """
        return self.get_queryset() \
            .filter(is_scheduled=False, **kwargs) \
            .order_by('subscription_id', 'buy_date') \
            .first()

    def try_to_schedule(self, teacher=None, date=None, entry=None, **kwargs):  # NOQA
        """
        Try to schedule a lesson, return a hash with errors or lesson otherwise
        In spite of its complicity, this method does only to things:
            1) Searches for bought class, that fits user choice
            2) Tries to assign it to a teachers timeline entry

        All the logic is for displaying errors.
        """

        """ Find a bought class with a lesson type of entry, trying to schedule """
        if entry is not None:
            kwargs['lesson_type'] = entry.lesson.contenttype()
        c = self.find_class(**kwargs)

        if not c:
            err = "You don't have available lessons"
            if kwargs.get('lesson_type'):
                lesson_type = kwargs.get('lesson_type')
                err = "You don't have available " + lesson_type.model_class()._meta.verbose_name_plural.lower()
            elif entry:
                err = "You don't have available " + entry.lesson._meta.verbose_name_plural.lower()

            return self.__result(
                result=False,
                error='E_CLASS_NOT_FOUND',
                text=err,
            )

        """ If a class (bought lesson) is found, the try to schedule it."""
        try:
            if entry is None:
                c.schedule(
                    teacher=teacher,
                    date=date
                )
            else:
                c.assign_entry(entry)

        except CannotBeScheduled:
            """
            Should not be thrown in normal circumstances. When you see this error,
            check the method :model:`hub.class`.can_be_scheduled() — there are all
            the reasons, that throw this excpetions. You can comment them one by one
            any find the reason.
            """
            return self.__result(
                result=False,
                error='E_CANT_SCHEDULE',
                text='Your choice does not fit teachers timeline'
            )
        return self.__result(result=True, c=c)

    def __result(self, result, error='E_NONE', text=None, c=None):
        return {
            'result': result,
            'error': error,
            'text': text,
            'c': c,
        }


class Class(BuyableProduct):
    """
    Represents a single bought lesson. When buying a class, one should
    store request in the `request` property of this instance. This is neeeded for
    the log entry to contain request data requeired for futher analysis.

    The property is accessed later in the history.signals module.
    """
    BUY_SOURCES = (
        (0, 'Single'),
        (1, 'Subscription')
    )

    objects = ClassesManager()

    customer = models.ForeignKey(Customer, related_name='classes')
    is_scheduled = models.BooleanField(default=False)
    buy_source = models.SmallIntegerField(choices=BUY_SOURCES, default=0)
    buy_date = models.DateTimeField(auto_now_add=True)

    lesson_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    lesson_id = models.PositiveIntegerField()
    lesson = GenericForeignKey('lesson_type', 'lesson_id')

    timeline_entry = models.ForeignKey(TimelineEntry, null=True, blank=True, related_name='classes')

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True, related_name='classes')

    class Meta:
        get_latest_by = 'buy_date'

    @property
    def name_for_user(self):
        return self.lesson.name

    def save(self, *args, **kwargs):
        """
        If timeline entry is assigned, change attribute is_scheduled to True, and
        add current customer to the customers list
        """
        if self.timeline_entry is not None:
            self.timeline_entry.save()
            self.is_scheduled = True
            if not self.timeline_entry.customers.filter(pk=self.customer.pk).exists():
                self.timeline_entry.customers.add(self.customer)
                self.timeline_entry.save()

        else:
            self.is_scheduled = False

        super().save(*args, **kwargs)

    def __str__(self):
        if self.subscription:
            return "#%d %s by %s for %s" % (self.pk, self.lesson, self.subscription.product, self.customer)
        return "#%d %s for %s" % (self.pk, self.lesson, self.customer)

    def assign_entry(self, entry):
        """
        Assign a timeline entry.
        """
        if not self.can_be_scheduled(entry):
            raise CannotBeScheduled('%s %s' % (self, entry))

        self.timeline_entry = entry

    def schedule(self, teacher, date, allow_overlap=True, allow_besides_working_hours=False):
        """
        Method for scheduling a lesson that does not require a timeline entry.
        allow_besides_working_hours should be set to True only when testing.
        """
        Lesson = type(self.lesson)
        if Lesson.timeline_entry_required():  # every lesson model should define if it requires a timeline entry or not. For details, see :model:`lessons.Lesson`
            raise CannotBeScheduled("Lesson '%s' requieres a teachers timeline entry" % self.lesson)

        entry = TimelineEntry(
            teacher=teacher,
            lesson=self.lesson,
            start=date,
            allow_besides_working_hours=allow_besides_working_hours,
            allow_overlap=allow_overlap,
        )

        self.assign_entry(entry)

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

        if not entry.allow_besides_working_hours and not entry.is_fitting_working_hours():
            return False

        return True
