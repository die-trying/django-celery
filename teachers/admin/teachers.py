from django.contrib import admin
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from suit.widgets import HTML5Input, SuitTimeWidget

from elk.admin import ModelAdmin, StackedInline, TabularInline
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
    list_display = ('__str__', 'CRM_profile', 'manualy_completed_classes', 'lessons_allowed')

    inlines = (WorkingHoursInline, GooogleCalendarInline)

    def manualy_completed_classes(self, instance):
        return instance.manualy_completed_classes.count()

    def lessons_allowed(self, instance):
        return instance.allowed_lessons.all().count()

    def CRM_profile(self, instance):
        return format_html('<a class="teacher_crm_profile" href="{url}">{name}</a>'.format(
            url=reverse('admin:crm_customer_change', args=[instance.user.crm.pk]),
            name=instance.user.crm.full_name,
        ))
