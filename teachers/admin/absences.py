from django.contrib import admin
from django.utils.translation import ugettext as _

from elk.admin import ModelAdmin
from teachers.models import Absence


class TeacherFilter(admin.SimpleListFilter):
    title = _('Teacher')
    parameter_name = 'teacher'

    def lookups(self, request, model_admin):
        return (
            [i.teacher.pk, str(i.teacher)] for i in Absence.objects.distinct('teacher')
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        return queryset.filter(teacher=self.value())


@admin.register(Absence)
class AbsenceAdmin(ModelAdmin):
    readonly_fields = ('is_approved',)
    list_display = ('teacher', 'type', 'start', 'end')
    list_filter = (TeacherFilter, 'type')
