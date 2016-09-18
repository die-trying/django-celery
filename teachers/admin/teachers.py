from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import capfirst
from suit.widgets import HTML5Input

from elk.admin import ModelAdmin, StackedInline, TabularInline
from extevents.models import ExternalEvent, GoogleCalendar
from manual_class_logging.models import ManualClassLogEntry
from teachers.models import Teacher, WorkingHours


class WorkingHoursInline(StackedInline):
    model = WorkingHours


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
        return ExternalEvent.objects \
            .filter(src_id=instance.pk) \
            .filter(src_type=ContentType.objects.get_for_model(instance)) \
            .count()

    class Media:
        css = {
            'all': ('admin/calendar_admin.css',),
        }


class ManualClassLogEntriesInline(TabularInline):
    model = ManualClassLogEntry
    readonly_fields = ('customer', 'lesson_type', 'completion_time')
    fieldsets = (
        (None, {'fields': ('customer', 'lesson_type', 'completion_time')}),
    )

    def customer(self, instance):
        return instance.Class.customer.full_name

    def lesson_type(self, instance):
        return capfirst(instance.Class.lesson_type.model_class()._meta.verbose_name)

    def completion_time(self, instance):
        return self._datetime(instance.timestamp)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Teacher)
class TeacherAdmin(ModelAdmin):
    list_display = ('__str__', 'manualy_completed_classes', 'lessons_allowed')

    inlines = (ManualClassLogEntriesInline, WorkingHoursInline, GooogleCalendarInline)

    def manualy_completed_classes(self, instance):
        return instance.manualy_completed_classes.count()

    def lessons_allowed(self, instance):
        return instance.allowed_lessons.all().count()
