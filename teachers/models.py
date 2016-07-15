from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Teacher(models.Model):
    """
    Represent options, specific to a teacher.
    Usualy accessable via `user.teacher_data`
    """
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='teacher_data', limit_choices_to={'is_staff': 1})

    def __str__(self):
        return '%s (%s)' % (self.user.crm.full_name, self.user.username)


class WorkingHours(models.Model):
    WEEKDAYS = (
        (1, _('Monday')),
        (2, _('Tuesday')),
        (3, _('Wednesday')),
        (4, _('Thursday')),
        (5, _('Friday')),
        (6, _('Saturday')),
        (7, _('Sunday')),
    )
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='working_hours')

    weekday = models.IntegerField('Weekday', choices=WEEKDAYS)
    start = models.TimeField('Start hour (UTC)')
    end = models.TimeField('End hoour(UTC)')

    def as_dict(self):
        return {
            'id': self.pk,
            'weekday': self.weekday,
            'start': str(self.start),
            'end': str(self.end)
        }

    def __str__(self):
        return '%s: day %d' % (self.teacher.user.username, self.weekday)

    class Meta:
        unique_together = ('teacher', 'weekday')
        verbose_name_plural = "Working hours"
