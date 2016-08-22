from django.contrib import admin
from elk.admin import ModelAdmin
from .models import ManualClassLogEntry
from crm.models import Customer


class StudentFilter(admin.SimpleListFilter):
    title = 'Student'
    parameter_name = 'customer'

    def lookups(self, request, model_admin):
        return [(i.pk, i.full_name) for i in Customer.objects.filter(classes__manualy_completed_classes__isnull=False).order_by('user__first_name', 'user__last_name').distinct()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            return queryset.filter(Class__customer=self.value())


class TeacherFilter(admin.SimpleListFilter):
    title = 'Teacher'
    parameter_name = 'teacher'

    def lookups(self, request, model_admin):
        return [(i.teacher.pk, i.teacher.user.crm.full_name) for i in ManualClassLogEntry.objects.distinct('teacher')]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            return queryset.filter(teacher=self.value())


@admin.register(ManualClassLogEntry)
class ManualClassLogEntryAdmin(ModelAdmin):
    list_filter = (StudentFilter, TeacherFilter)
    list_display = ('date', 'lesson_type', 'student', 'teacher',)
    readonly_fields = ('teacher', 'Class')

    def date(self, instance):
        return self._datetime(instance.timestamp) + ' ' + self._time(instance.timestamp)

    date.admin_order_field = 'timestamp'

    def lesson_type(self, instance):
        return instance.Class.lesson_type.model_class()._meta.verbose_name

    def student(self, instance):
        return instance.Class.customer.full_name

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
