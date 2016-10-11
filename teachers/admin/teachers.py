from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from suit.widgets import HTML5Input, SuitTimeWidget

from elk.admin import ModelAdmin, StackedInline, TabularInline
from elk.templatetags.skype import skype_chat
from extevents.models import ExternalEvent, GoogleCalendar
from teachers.models import Teacher, WorkingHours


class WorkingHoursInline(StackedInline):
    model = WorkingHours
    verbose_name = 'Weekday'
    verbose_name_plural = 'Comfortable hours'
    formfield_overrides = {
        models.TimeField: {'widget': SuitTimeWidget(attrs={'placeholder': '16:45', 'maxlength': '5', 'class': 'numonly'})}
    }


class GooogleCalendarInline(TabularInline):
    model = GoogleCalendar
    fields = ('url', 'updated', 'found_events')
    readonly_fields = ('updated', 'found_events')
    extra = 1

    formfield_overrides = {
        models.URLField: {'widget': HTML5Input(input_type='url', attrs={'placeholder': 'Private Google calendar URL'})},
    }

    def updated(self, instance):
        return self._datetime(instance.last_update)

    def found_events(self, instance):
        return ExternalEvent.objects.by_src(instance).count()

    class Media:
        css = {
            'all': ('admin/calendar_admin.css',),
        }


@admin.register(Teacher)
class TeacherAdmin(ModelAdmin):
    list_display = ('__str__', 'CRM_profile', 'email', 'skype', 'month_class_count', 'lessons_allowed')

    inlines = (WorkingHoursInline, GooogleCalendarInline)

    def month_class_count(self, instance):
        completed_class_count = instance.accounting_events.filter(event_type='class')\
            .filter(timestamp__gte=timezone.now().replace(day=1)).count()
        if not completed_class_count:
            return '—'

        return format_html('<a href="{url}?timestamp_start={start}&timestamp_end={end}&teacher__id__exact={teacher_id}">{count}</a>'.format(
            url=reverse('admin:accounting_event_changelist'),
            teacher_id=instance.pk,
            count=completed_class_count,
            start=timezone.now().replace(day=1).strftime('%Y-%m-%d'),
            end=timezone.now().strftime('%Y-%m-%d'),
        ))

    def lessons_allowed(self, instance):
        return instance.allowed_lessons.all().count()

    def CRM_profile(self, instance):
        return format_html('<a href="{url}">{name}</a>'.format(
            url=reverse('admin:crm_customer_change', args=[instance.user.crm.pk]),
            name=instance.user.crm.full_name,
        ))

    def email(self, instance):
        return format_html('<a href="mailto:{email}">{email}</a>'.format(email=instance.user.email))

    def skype(self, instance):
        skype = instance.user.crm.skype
        if not skype:
            return '—'
        return format_html(skype_chat(instance.user.crm))
