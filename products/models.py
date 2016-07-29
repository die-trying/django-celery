from datetime import timedelta

from django.db import models
from djmoney.models.fields import MoneyField

from lessons.models import HappyHour, LessonWithNative, MasterClass, OrdinaryLesson, PairedLesson


# Create your models here.


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
