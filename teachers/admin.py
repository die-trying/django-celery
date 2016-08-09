from django.contrib import admin

from elk.utils.admin import ModelAdmin
from teachers.models import Teacher, WorkingHours


class WorkingHoursInline(admin.StackedInline):
    model = WorkingHours


@admin.register(Teacher)
class TeacherAdmin(ModelAdmin):
    inlines = (WorkingHoursInline,)
