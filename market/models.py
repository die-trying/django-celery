from abc import abstractproperty
from datetime import timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField

from crm.models import Customer
from elk.logging import logger
from market.exceptions import CannotBeScheduled
from market.signals import class_cancelled, class_scheduled
from teachers.models import PLANNING_DELTA
from timeline.models import Entry as TimelineEntry

MARK_CLASSES_AS_USED_AFTER = timedelta(hours=1)


class BuyableProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=1)


class BuyableProduct(models.Model):
    """
    Parent of every buyable object
    """
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )

    buy_date = models.DateTimeField(auto_now_add=True)
    buy_price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    is_fully_used = models.BooleanField(default=False, db_index=True)
    active = models.SmallIntegerField(choices=ENABLED, default=1, db_index=True)

    @abstractproperty
    def name_for_user(self):
        pass

    def delete(self):
        """
        Disable deletion for any buyable thing
        """
        self.active = 0
        self.save()

    def mark_as_fully_used(self):
        """
        Mark product as fully used. Caution — does automatic save!
        """
        self.is_fully_used = True
        self.save()

    def renew(self):
        """
        Make a brand-new class, like it was never used before
        """
        self.is_fully_used = False
        self.timeline = None
        self.save()

    class Meta:
        abstract = True
        ordering = ('buy_date',)


class SubscriptionManager(BuyableProductManager):
    use_for_related_fields = True

    def active(self):
        return self.get_queryset() \
            .filter(is_fully_used=False) \
            .first()


class Subscription(BuyableProduct):
    """
    Represents a single purchased subscription.

    When buying a subscription, one should store request in the `request`
    property of this instance. This is neeed for the log entry to contain
    request data requeired for futher analysis.

    The property is accessed later in the history.signals module.
    """
    objects = SubscriptionManager()
    customer = models.ForeignKey(Customer, related_name='subscriptions', db_index=True)

    product_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'app_label': 'products'})
    product_id = models.PositiveIntegerField(default=1)  # flex scope — always add the first product
    product = GenericForeignKey('product_type', 'product_id')

    def __str__(self):
        return self.name_for_user

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
        for lesson_type in self.product.lesson_types():
            for lesson in self.product.classes_by_lesson_type(lesson_type):
                c = Class(
                    lesson=lesson,
                    subscription=self,
                    customer=self.customer,
                    buy_price=self.buy_price,
                    buy_source='subscription',  # store a sign, that class is purchased by subscription
                )
                if hasattr(self, 'request'):
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

    def check_is_fully_finished(self):
        """
        Check, if subscription has unused classes. If not — mark self as fully_used
        """
        if self.classes.filter(is_fully_used=False).exists():
            return
        else:
            self.mark_as_fully_used()

    def class_status(self):
        """
        Get statistics about classes, purchased via subscription instance.
        """
        results = []
        for lesson_type in self.product.lesson_types():
            classes = self.classes
            r = {
                'name': lesson_type.model_class()._meta.verbose_name_plural,
                'available': classes.available().filter(lesson_type=lesson_type).count(),
                'used': classes.used().filter(lesson_type=lesson_type).count(),
                'scheduled': classes.scheduled().filter(lesson_type=lesson_type).count(),
            }
            r['used_and_scheduled'] = r['used'] + r['scheduled']
            results.append(r)
        return results

    def is_fresh_and_shiny(self):
        """
        Returns true if subscription should be displayed as new
        """
        if self.classes.filter(is_scheduled=True).count():
            return False
        if self.classes.filter(is_fully_used=True).count():
            return False
        return True


class ClassesManager(BuyableProductManager):
    """
    Almost all of this methods assume, that they are called from a related
    manager customer.classes, like customer.classes.nearest()
    """
    def nearest_scheduled(self, **kwargs):
        """
        Return nearest scheduled class
        """
        date = self.__now()
        if 'date' in kwargs:
            date = kwargs['date']
            del kwargs['date']

        return self.get_queryset() \
            .filter(is_scheduled=True, timeline__start__gte=date) \
            .filter(**kwargs) \
            .order_by('timeline__start') \
            .first()

    def starting_soon(self, delta):
        """
        Return a queryset with classes, that are about to start in `delta` time.

        Delta is a python datetime.timedelta.
        """
        print(self.__now() + delta)

        return self.get_queryset() \
            .filter(is_scheduled=True) \
            .filter(timeline__start__range=(self.__now(), self.__now() + delta))

    def purchased_lesson_types(self):
        """
        Get ContentTypes of lessons, available to user
        """
        types = self.get_queryset().filter(is_scheduled=False).values_list('lesson_type', flat=True).distinct()

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

        return [sort_order[i] for i in sorted(sort_order.keys())]

    def find_student_classes(self, lesson_type):
        """
        Find students, that can schedule a lesson_type
        """
        return self.get_queryset() \
            .filter(is_scheduled=False, is_fully_used=False) \
            .filter(lesson_type=lesson_type) \
            .distinct('customer')

    def dates_for_planning(self):
        """
        A generator of dates, available for planning for particular user

        If current time + planning delta is more then 00:00 then the first day is tomorrow
        """
        current = timezone.now()

        if timezone.localtime(current + PLANNING_DELTA).day != timezone.localtime(current).day:
            current += timedelta(days=1)

        for i in range(0, 14):
            yield current
            current += timedelta(days=1)

    def used(self):
        return self.get_queryset().filter(is_fully_used=True)

    def available(self):
        return self.get_queryset().filter(is_fully_used=False)

    def scheduled(self):
        return self.get_queryset().filter(is_fully_used=False, is_scheduled=True)

    def __now(self):
        return timezone.now()


class Class(BuyableProduct):
    """
    Represents a single purchased lesson.

    Purpose
    =======
    Incapsulate all low-level scheduling logic. High level logic is
    located in the SortingHat — if you want to plan a lesson for the
    particular student, please use the hat.

    Storing a request
    =================
    When buying a class, one should store request in the `request`
    property of this instance. This is neeeded for the log entry to
    contain request data requeired for futher analysis.

    The property is accessed later in the history.signals module.

    Deleting a class
    ================
    Currently we need posibility to unschedule a class through django-admin.
    This is done by deleting — the classs delete() method checks, if class is
    scheduled, and if it is, delete() just un-schedules it.

    For backup purposes, the delete method is redefined in :model:`market.BuyableProduct`
    for completely disabling deletion of anything, that anyone has purchased for money.
    """
    objects = ClassesManager()

    customer = models.ForeignKey(Customer, related_name='classes', db_index=True)
    is_scheduled = models.BooleanField(default=False)

    buy_source = models.CharField(max_length=12, default='single')

    lesson_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'app_label': 'lessons'})
    lesson_id = models.PositiveIntegerField()
    lesson = GenericForeignKey('lesson_type', 'lesson_id')

    timeline = models.ForeignKey(TimelineEntry, null=True, blank=True, on_delete=models.SET_NULL, related_name='classes')

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True, related_name='classes')

    pre_start_notifications_sent_to_teacher = models.BooleanField(default=False)
    pre_start_notifications_sent_to_student = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Purchsed lesson'
        get_latest_by = 'buy_date'

    @property
    def name_for_user(self):
        return self.lesson.name

    @property
    def finish_time(self):
        if not self.is_fully_used:
            return None

        if self.timeline is not None:
            return self.timeline.start

        if self.manualy_completed_classes.first() is not None:
            return self.manualy_completed_classes.first().timestamp

        logger.warning('Tried to check finished class without a finished date')

    def save(self, *args, **kwargs):
        self.__set_default_lesson_id_if_required()

        if self.timeline is None:
            return self._save_unscheduled(*args, **kwargs)
        return self._save_scheduled(*args, **kwargs)

    def mark_as_fully_used(self):
        """
        Notify a parent subscription, that it might be fully used
        """
        super().mark_as_fully_used()
        if self.subscription:
            self.subscription.check_is_fully_finished()

    def _save_scheduled(self, *args, **kwargs):
        """
        Save a class with assigned timeline entry.

        If entry is a new one, save() it before saving ourselves.
        """
        was_scheduled = self.is_scheduled

        self.is_scheduled = True

        if not self.timeline.pk:  # this happens when the entry is created in current iteration
            self.timeline.save()
            """
            We do not use self.assign_entry() method here, because we assume, that
            all required checks have passed. In future there may be cases, when
            we should re-save a class with an invalid timeline entry. If we re-run
            all checks, we will not be able to do this
            """
            self.timeline = self.timeline

        super().save(*args, **kwargs)

        """
        Below we run save() on an entry one more time. This is needed for
        an ability to run save() only on a class, without a need to run save()
        also on an entry.

        This is usefull when instance of Class is created within the same
        iteration with a timeline entry, i.e. when scheduling through the
        sorting hat.
        """
        self.timeline.save()

        """ If the class was scheduled for the first time — send a signal """
        if not was_scheduled:
            class_scheduled.send(sender=self.__class__, instance=self)

        """ Nullify customer cancellation_streak """
        # self.customer.cancellation_streak = 0
        # self.customer.save()
        """
        Nullification is disabled, because it should be done asyncronously,
        when user has some actualy passed classes two las weeks
        """

    def _save_unscheduled(self, *args, **kwargs):
        """
        Save a class without an assigned timeline entry.

        Handle a case when save() is invoked when a timeline entry is deleted
        from a class. We need this for ability to edit a class from django-admin.
        """
        self.is_scheduled = False
        if kwargs.get('update_fields') and 'timeline_entry' in kwargs['update_fields']:
            old_entry = Class.objects.get(pk=self.pk).timeline
            super().save(*args, **kwargs)
            old_entry.save()

        super().save(*args, **kwargs)

    def __set_default_lesson_id_if_required(self):
        """
        When saving a class with defined lesson_type and without defined lesson_id
        we set the default lesson
        """
        if self.lesson_type and not self.lesson_id:
            self.lesson = self.lesson_type.model_class().get_default()

    def delete(self):
        """
        This method provides an ability to unschedule a class via deletion.

        It may be looking weired, but this is the only way to unschedule a class
        throught django-admin. For more details see model description and :model:`market.BuyableProduct`
        """
        if self.is_scheduled:
            self.cancel()
            self.save()
        else:
            super().delete()

    def __str__(self):
        s = "{lesson} for {student}".format(lesson=self.lesson.internal_name, student=self.customer)
        if self.subscription:
            s += " (%s)" % self.subscription.product
        return s

    def assign_entry(self, entry):
        """
        Assign a timeline entry.
        """
        if not self.can_be_scheduled(entry):
            raise CannotBeScheduled('%s %s' % (self, entry))
        self.timeline = entry
        self.timeline.clean()

    def schedule(self, **kwargs):
        """
        Method for scheduling a lesson that does not require a timeline entry.
        allow_besides_working_hours should be set to True only when testing.
        """
        Lesson = type(self.lesson)
        if Lesson.timeline_entry_required():  # every lesson model should define if it requires a timeline entry or not. For details, see :model:`lessons.Lesson`
            raise CannotBeScheduled("Lesson '%s' requieres a teachers timeline entry" % self.lesson)

        entry = self.__get_entry(**kwargs)
        self.assign_entry(entry)

    def __get_entry(self, teacher, date, allow_overlap=True, allow_besides_working_hours=False):
        """
        Find existing timeline entry or create a new one for lessons, that don't require
        a particular timeline entry.
        """
        try:
            return TimelineEntry.objects.get(
                teacher=teacher,
                lesson_type=self.lesson.get_contenttype(),
                start=date
            )
        except TimelineEntry.DoesNotExist:
            return TimelineEntry(
                teacher=teacher,
                lesson=self.lesson,
                start=date,
                allow_besides_working_hours=allow_besides_working_hours,
                allow_overlap=allow_overlap,
            )

    def cancel(self, src='teacher', request=None):
        """
        Unschedule previously scheduled lesson
        """
        if src == 'customer':
            if self.timeline.start < timezone.now():
                raise ValidationError('Past classes cannot be cancelled')
            self.customer.cancellation_streak += 1
            self.customer.save()

        if src != 'dangerous-cancellation' and (self.timeline.start + MARK_CLASSES_AS_USED_AFTER) < timezone.now():  # teachers can cancel classes even after they started
            raise ValidationError('Past classes cannot be cancelled')

        class_cancelled.send(sender=self.__class__, instance=self, src=src)

        entry = self.timeline
        entry.classes.remove(self, bulk=True)  # expcitly disable running of self.save()
        self.renew()
        entry.save()

    def can_be_scheduled(self, entry):
        """
        Check if timeline entry can be scheduled

        TODO: This method should raise exceptions for each situation,
        when a class cannot be scheduled
        """
        if self.is_scheduled or not entry.is_free:
            return False

        if self.lesson_type != entry.lesson_type:
            return False

        try:
            entry.clean()
        except ValidationError:
            """
            If you can see this error, please investigate the way timenetry was crated by.
            Possibly there is a place in the system, that generates unschedulable timeline entries.
            """
            logger.error("Timeline entry can't be scheduled")
            return False

        return True

    def can_be_unscheduled(self):
        if self.timeline.is_in_past():
            return False

        return True
