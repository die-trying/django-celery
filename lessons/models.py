from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django_markdown.models import MarkdownField


# Create your models here.


class Lesson(models.Model):
    """
    Abstract class for generic lesson, defined properties for all lessons

    Represents a lesson type, that user can buy — ordinary lesson, master class,
    etc.
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

    def as_dict(self):
        """Dicitionary representation of a lesson"""
        return {
            'id': self.pk,
            'name': self.internal_name,
            'duration': str(self.duration)
        }

    class Meta:
        abstract = True


class HostedLesson(Lesson):
    """
    Abstract class for generic lesson, that requires a host, i.e. Master class
    or ELK Happy hour
    """
    host = models.ForeignKey(User, limit_choices_to={'is_staff': 1}, related_name='+', null=True)

    class Meta:
        abstract = True


class OrdinaryLesson(Lesson):

    class Meta:
        verbose_name = "Usual curated lesson"


class LessonWithNative(Lesson):

    class Meta:
        verbose_name = "Curataed lesson with native speaker"
        verbose_name_plural = "Curated lessons with native speaker"


class MasterClass(HostedLesson):

    @classmethod
    def get_default(cls):
        raise NotImplementedError('You can not buy a default master class, sorry')

    class Meta:
        verbose_name = "Master Class"
        verbose_name_plural = "Master Classes"


class HappyHour(HostedLesson):

    @classmethod
    def get_default(cls):
        raise NotImplementedError('You can not buy a default master class, sorry')

    class Meta:
        verbose_name = "Happy Hour"


class PairedLesson(Lesson):

    class Meta:
        verbose_name = "Paired Lesson"
