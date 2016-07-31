from django.contrib import admin
from django.utils.html import format_html

from hub.models import Class

from .models import Entry as TimelineEntry


# Register your models here.


class ClassInline(admin.StackedInline):
    model = Class
    verbose_name = 'Student'
    verbose_name_plural = 'Assigned students'
    readonly_fields = ('customer',)
    fieldsets = (
        (None, {
            'fields': ('customer',)
        }),
    )

    def has_add_permission(self, request):
        return False


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    readonly_fields = ('slots', 'taken_slots', 'start', 'lesson', 'students', 'teacher')
    list_display = ('teacher', 'start', 'duration', 'is_free')
    inlines = (ClassInline,)
    fieldsets = (
        ('Planned lesson', {
            'fields': ('start', 'students'),
        }),
        ('Lesson', {
            'fields': ('teacher', 'lesson'),
        }),
    )

    def duration(self, instance):
        d = str(instance.end - instance.start).split(':')

        if len(d[0]) < 2:
            d[0] = '0%s' % d[0]

        return '%s:%s' % (d[0], d[1])

    def lesson(self, instance):
        return format_html('<a href = "%s">%s</a>' % (instance.lesson.admin_url, instance.lesson.internal_name))

    def students(self, instance):
        return "%s/%s" % (instance.taken_slots, instance.slots)
