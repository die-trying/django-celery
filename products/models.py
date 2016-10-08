from datetime import timedelta

from django.db import models
from djmoney.models.fields import MoneyField

from lessons.models import HappyHour, LessonWithNative, MasterClass, OrdinaryLesson, PairedLesson


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


class ProductWithLessons(Product):
    """
    Base class for products that contain lessons.

    Please don't use admin for managing lessons of particular product —
    use the migrations. Example migration you can find ad products/migrations/0002_simplesubscription.py
    """
    def lessons(self):
        """
        Get all lesson attributes of a subscription
        """
        for i in self.LESSONS:
            yield getattr(self, i)

    def lesson_types(self):
        """
        Get ContentTypes of lessons, that are included in the product
        """
        for bundled_lesson in self.lessons():
            yield bundled_lesson.model.get_contenttype()

    def classes_by_lesson_type(self, lesson_type):
        """
        Get all lessons in subscription by contenttype
        """
        for bundled_lesson in self.lessons():
            if bundled_lesson.model.get_contenttype() == lesson_type:
                return bundled_lesson.all()

    class Meta:
        abstract = True


class Product1(ProductWithLessons):
    """
    Stores information about subscriptions of the first type.
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


class SimpleSubscription(ProductWithLessons):
    """
    Simple subscription for beginners
    """
    LESSONS = (
        'ordinary_lessons',
        'lessons_with_native',
        'paired_lessons',
    )
    ordinary_lessons = models.ManyToManyField(OrdinaryLesson, limit_choices_to={'active': 1})
    paired_lessons = models.ManyToManyField(PairedLesson, limit_choices_to={'active': 1})
    lessons_with_native = models.ManyToManyField(LessonWithNative, limit_choices_to={'active': 1})

    class Meta:
        verbose_name = "Subscription type: beginners subscription"
        verbose_name_plural = "Beginner subscriptions"
