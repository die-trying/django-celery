from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_markdown.models import MarkdownField

from teachers.models import Teacher


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
    def contenttype(cls):
        """
        Shortcut for getting ContentType of current lesson
        """
        return ContentType.objects.get_for_model(cls)

    @classmethod
    def can_be_directly_planned(cls):
        """
        Can lessons of this type be planned directly by user. For example this is
        false for Paired lesson — only system can plan them.
        """
        return True

    @classmethod
    def timeline_entry_required(cls):
        """
        Does this lesson type require a timeline entry
        """
        return False

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
            'slots': self.slots,
            'duration': str(self.duration)
        }

    class Meta:
        abstract = True


class HostedLesson(Lesson):
    """
    Abstract class for generic lesson, that requires a host, i.e. Master class
    or ELK Happy hour
    """
    host = models.ForeignKey(Teacher, related_name='+', null=True)

    @classmethod
    def timeline_entry_required(cls):
        """
        All hosted lessons require planning
        """
        return True

    def save(self, *args, **kwargs):
        """
        Check if assigned teacher is allowed to host this event type.
        """
        if self.host is not None:
            my_content_type = ContentType.objects.get_for_model(self)
            try:
                self.host.acceptable_lessons.get(pk=my_content_type.pk)
            except:
                raise ValidationError('Teacher %s can not accept lesson %s' % (self.host, my_content_type))

            else:
                super().save(*args, **kwargs)

    @classmethod
    def get_default(cls):
        raise NotImplementedError('You can not buy a default master class, sorry')

    class Meta:
        abstract = True


class OrdinaryLesson(Lesson):

    class Meta(Lesson.Meta):
        verbose_name = _("Curated session")


class LessonWithNative(Lesson):

    class Meta(Lesson.Meta):
        verbose_name = _("Native speaker session")
        verbose_name_plural = _("Native speakers")


class MasterClass(HostedLesson):

    class Meta(HostedLesson.Meta):
        verbose_name = _("Master Class")
        verbose_name_plural = _("Master Classes")


class HappyHour(HostedLesson):

    class Meta(HostedLesson.Meta):
        verbose_name = _("Happy Hour")


class PairedLesson(Lesson):

    @classmethod
    def can_be_directly_planned(cls):
        """ Paired lessons can't be planned by user """
        return False

    class Meta(Lesson.Meta):
        verbose_name = _("Paired Lesson")
