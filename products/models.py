from abc import abstractmethod
from datetime import timedelta

from django.db import models
from django_markdown.models import MarkdownField
from djmoney.models.fields import MoneyField
from django.contrib.contenttypes.fields import GenericRelation

from hub.models import ActiveSubscription

# Create your models here.


class Lesson(models.Model):
    name = models.CharField(max_length=140)
    internal_name = models.CharField(max_length=140)

    duration = models.DurationField(default=timedelta(minutes=30))
    description = MarkdownField()

    def __str__(self):
        return self.internal_name

    @staticmethod
    @abstractmethod
    def get_default():
        raise NotImplementedError('Every lesson should implement `get_default()` static method for buing a single lesson')

    class Meta:
        abstract = True


class OrdinaryLesson(Lesson):

    def get_default():
        return OrdinaryLesson.objects.get(pk=500)


class LessonWithNative(Lesson):
    def get_default():
        return LessonWithNative.objects.get(pk=500)


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
    LESSONS = ('ordinary_lessons', 'lessons_with_native')

    ordinary_lessons = models.ManyToManyField(OrdinaryLesson, limit_choices_to={'active': 1})
    lessons_with_native = models.ManyToManyField(LessonWithNative)
