from datetime import timedelta

from django.db import models
from django_markdown.models import MarkdownField
from djmoney.models.fields import MoneyField
from django.contrib.contenttypes.fields import GenericRelation

from hub.models import ActiveSubscription

# Create your models here.


class Lesson(models.Model):
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )
    name = models.CharField(max_length=140)
    internal_name = models.CharField(max_length=140)

    duration = models.DurationField(default=timedelta(minutes=30))
    description = MarkdownField()

    active = models.IntegerField(default=1, choices=ENABLED)

    def __str__(self):
        return self.internal_name

    @classmethod
    def get_default(cls):
        return cls.objects.get(pk=500)

    class Meta:
        abstract = True


class OrdinaryLesson(Lesson):

    class Meta:
        verbose_name = "Usual curated lesson"


class LessonWithNative(Lesson):
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
    LESSONS = ('ordinary_lessons', 'lessons_with_native')

    ordinary_lessons = models.ManyToManyField(OrdinaryLesson, limit_choices_to={'active': 1})
    lessons_with_native = models.ManyToManyField(LessonWithNative, limit_choices_to={'active': 1})

    class Meta:
        verbose_name = "Subscription type: first subscription"
        verbose_name_plural = "Subscriptions of the first type"
