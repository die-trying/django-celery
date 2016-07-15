from django.contrib import admin

from teachers.models import Teacher, WorkingHours


class WorkingHoursInline(admin.StackedInline):
    model = WorkingHours


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    inlines = (WorkingHoursInline,)
