from django.contrib import admin
from django.template.defaultfilters import capfirst
from django.utils.dateformat import format

from elk.admin import ModelAdmin, TabularInline
from manual_class_logging.models import ManualClassLogEntry
from teachers.models import Teacher, WorkingHours


class WorkingHoursInline(admin.StackedInline):
    model = WorkingHours


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
        return capfirst(format(instance.timestamp, 'b d h:m a'))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Teacher)
class TeacherAdmin(ModelAdmin):
    list_display = ('__str__', 'manualy_completed_classes', 'lessons_allowed')

    inlines = (ManualClassLogEntriesInline, WorkingHoursInline)

    def manualy_completed_classes(self, instance):
        return instance.manualy_completed_classes.count()

    def lessons_allowed(self, instance):
        return instance.allowed_lessons.all().count()
