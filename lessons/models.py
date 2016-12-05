from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_markdown.models import MarkdownField


class Language(models.Model):
    """
    Language that teacher can teach and customer can learn.
    """
    name = models.CharField(max_length=140)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Lesson(models.Model):
    """
    Abstract class for generic lesson, defined properties for all lessons

    Represents a lesson type, that user can buy — ordinary lesson, master class,
    etc.

    Lesson types have plenty of class properties, hardcoded for fine inheriting.
    Here they are:

    - can_be_directly_planned(): lesson, returning False, could not be planned by user
    - sort_order(): order for sorting lesson types in filters and other. Lessons, not defining order, are not shown.
    - timeline_entry_required(): lesson requires a specialy crafted entry in teachers timeline. True by defult for all hosted lessons.
    - get_default(): should return an instance of default lesson of type. By default raises NonImplemented for all hosted lessons.
    """
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )
    name = models.CharField(max_length=140)
    internal_name = models.CharField(max_length=140)

    duration = models.DurationField(default=timedelta(minutes=30))
    announce = MarkdownField()
    description = MarkdownField()

    slots = models.SmallIntegerField(default=1)

    active = models.IntegerField(default=1, choices=ENABLED)

    def __str__(self):
        return self.internal_name

    @property
    def type_verbose_name(self):
        return _(self.__class__._meta.verbose_name.lower())

    @classmethod
    def long_name(cls):
        if hasattr(cls, '_long_name'):
            return cls._long_name

        return _(cls._meta.verbose_name)

    @classmethod
    def long_name_plural(cls):
        if hasattr(cls, '_long_name_plural'):
            return cls._long_name_plural

        return _(cls._meta.verbose_name_plural)

    @classmethod
    def get_contenttype(cls):
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
        Does this lesson type require a timeline entry in teachers timeline. If
        not, :model:`market.Class` will create it automatically.
        """
        return False

    @classmethod
    def get_default(cls):
        """
        Every lesson should have a default record. User happens to buy lesson
        with this id when he buys a generic lesson of a type.

        By default this lesson id is 500. All default lessons are located in
        `lessons.yaml` fixture. When defining a new lesson type, fill free to add
        it to the fixture.

        If a lesson can't be purchased this way, it should raise a NotImplementedError,
        for example see `MasterClass` lesson.
        """
        return cls.objects.get(pk=500)

    @classmethod
    def sort_order(cls):
        """
        Every lesson should return an integer of its sorting order, used in filters. etc.

        For usage example, see :model:`market.Class` manager.
        """
        return None

    class Meta:
        abstract = True


class HostedLesson(Lesson):
    """
    Abstract class for generic lesson, that requires a host, i.e. Master class
    or ELK Happy hour
    """
    host = models.ForeignKey('teachers.Teacher', related_name='+', null=True)

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
                self.host.allowed_lessons.get(pk=my_content_type.pk)
            except:
                raise ValidationError('Teacher %s can not accept lesson %s' % (self.host, my_content_type))

            else:
                super().save(*args, **kwargs)

    class Meta:
        abstract = True


class OrdinaryLesson(Lesson):
    _long_name = _('Curated lesson')
    _long_name_plural = _('Curated lessons')

    @classmethod
    def sort_order(cls):
        return 100

    class Meta(Lesson.Meta):
        verbose_name = _("Single lesson")
        verbose_name_plural = _("Single lessons")


class TrialLesson(Lesson):
    @classmethod
    def sort_order(cls):
        return 999

    class Meta(Lesson.Meta):
        verbose_name = _('First lesson')


class LessonWithNative(Lesson):
    _long_name = _('Individual lesson with native speaker')
    _long_name_plural = _('Individual lessons with native speaker')

    @classmethod
    def sort_order(cls):
        return 300

    class Meta(Lesson.Meta):
        verbose_name = _("Native speaker")
        verbose_name_plural = _("Native speaker sessions")


class MasterClass(HostedLesson):
    _long_name = _('Round table')
    _long_name_plural = _('Round table')

    @classmethod
    def sort_order(cls):
        return 400

    class Meta(HostedLesson.Meta):
        verbose_name = _("Round table")
        verbose_name_plural = _("Round table")


class HappyHour(HostedLesson):
    _long_name = _('Happy hour session (5 students speaking to each other)')
    _long_name_plural = _('Happy hour sessions (5 students speaking to each other)')

    @classmethod
    def sort_order(cls):
        return 500

    class Meta(HostedLesson.Meta):
        verbose_name = _("Happy Hour")


class PairedLesson(HostedLesson):
    _long_name = _('Paired lesson with native speaker')
    _long_name_plural = _('Paired lessons with native speaker')

    @classmethod
    def sort_order(cls):
        return 200

    class Meta(Lesson.Meta):
        verbose_name = _("Paired lesson")
        verbose_name_plural = ("Paired lessons")
