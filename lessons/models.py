from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django_markdown.models import MarkdownField

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

    class Meta:
        verbose_name = "Curataed lesson with native speaker"
        verbose_name_plural = "Curated lessons with native speaker"


class MasterClass(Lesson):

    @classmethod
    def get_default(cls):
        raise NotImplementedError('You can not buy a default master class, sorry')

    class Meta:
        verbose_name = "Master Class"
        verbose_name_plural = "Master Classes"


class HappyHour(Lesson):

    @classmethod
    def get_default(cls):
        raise NotImplementedError('You can not buy a default master class, sorry')

    class Meta:
        verbose_name = "Happy Hour"


class PairedLesson(Lesson):

    class Meta:
        verbose_name = "Paired Lesson"


class Event(models.Model):
    """
    Represents an event type — Master class or ELK Happy Hour
    """
    lesson_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'app_label': 'lessons'})

    slots = models.SmallIntegerField(default=1)

    name = models.CharField(max_length=140)
    internal_name = models.CharField(max_length=140)
    host = models.ForeignKey(User, limit_choices_to={'is_staff': 1}, related_name='hosted_events')
    description = MarkdownField()
    duration = models.DurationField(default=timedelta(minutes=30))

    def __str__(self):
        return '%s: %s' % (self.lesson_type, self.internal_name)
