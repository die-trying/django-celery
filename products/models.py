from datetime import timedelta

from django.db import models
from django_markdown.models import MarkdownField
from djmoney.models.fields import MoneyField
from django.contrib.contenttypes.fields import GenericRelation

from hub.models import ActiveSubscription

# Create your models here.


class Lesson(models.Model):
    """
    Abstract class for generic lesson, defined properties for all lessons
    """
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )
    name = models.CharField(max_length=140)
    internal_name = models.CharField(max_length=140)

    duration = models.DurationField(default=timedelta(minutes=30))
    description = MarkdownField()

    slots = models.SmallIntegerField(default=1)

    active = models.IntegerField(default=1, choices=ENABLED)

    def __str__(self):
        return self.internal_name

    @classmethod
    def get_default(cls):
        """
        Every lesson should have a default record. User happens to buy lesson
        with this id when he buys a generic lesson of a type.

        By default this lesson id is 500.

        If a lesson can't be bought this way, it should raise a NotImplementedError,
        for example see `MasterClass` lesson.
        """
        return cls.objects.get(pk=500)

    class Meta:
        abstract = True


class OrdinaryLesson(Lesson):

    class Meta:
        verbose_name = "Usual curated lesson"


class LessonWithNative(Lesson):
    pass


class MasterClass(Lesson):

    @classmethod
    def get_default(cls):
        raise NotImplementedError('You can not buy a default master class, sorry')


class HappyHour(Lesson):
    pass


class PairedLesson(Lesson):
    pass


class Product(models.Model):
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )

    active = models.IntegerField(default=1, choices=ENABLED)
    cost = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    name = models.CharField(max_length=140)
    internal_name = models.CharField(max_length=140)

    duration = models.DurationField(default=timedelta(days=7 * 6))

    active_subscriptions = GenericRelation(ActiveSubscription)

    def __str__(self):
        return self.internal_name

    class Meta:
        abstract = True


class Product1(Product):
    """
    Stores information about subscriptions of the first type. You can admindocs
    desired lessons in the model administration.
    """
    LESSONS = (
        'ordinary_lessons',
        'lessons_with_native',
        'paired_lessons',
        'happy_hours',
        'master_classes'
    )

    ordinary_lessons = models.ManyToManyField(OrdinaryLesson, limit_choices_to={'active': 1})
    lessons_with_native = models.ManyToManyField(LessonWithNative, limit_choices_to={'active': 1})
    paired_lessons = models.ManyToManyField(PairedLesson, limit_choices_to={'active': 1})
    happy_hours = models.ManyToManyField(HappyHour, limit_choices_to={'active': 1})
    master_classes = models.ManyToManyField(MasterClass, limit_choices_to={'active': 1})

    class Meta:
        verbose_name = "Subscription type: first subscription"
        verbose_name_plural = "Subscriptions of the first type"
