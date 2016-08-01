from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db.models import F
from django.template.defaultfilters import capfirst
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from hub.models import Class

from .models import Entry as TimelineEntry


class ClassInline(admin.StackedInline):
    model = Class
    verbose_name = 'Bought lesson'
    verbose_name_plural = 'Assigned students'
    readonly_fields = ('customer',)
    fieldsets = (
        (None, {
            'fields': ('customer',)
        }),
    )

    def has_add_permission(self, request):
        return False


class LessonFilter(admin.SimpleListFilter):
    title = _('Lesson type')
    parameter_name = 'lesson_type'

    def lookups(self, request, model_admin):
        options = []
        for i in ContentType.objects.filter(app_label='lessons').values_list('pk', flat=True):
            options.append(
                (i, ContentType.objects.get(pk=i).model_class()._meta.verbose_name)
            )
        return options

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(lesson_type=self.value())
        else:
            return queryset


class FreeFilter(admin.SimpleListFilter):
    title = _('Has free slots left')
    parameter_name = 'is_free'

    def lookups(self, request, model_admin):
        return (
            ('t', 'Yes'),
            ('f', 'No'),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            if self.value() == 't':
                return queryset.filter(taken_slots__lt=F('slots'))
            else:
                return queryset.filter(slots=F('taken_slots'))


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    actions = []
    readonly_fields = ('slots', 'taken_slots', 'date', 'lesson', 'students', 'teacher')
    list_display = ('teacher', 'lesson_name', 'date', 'students')
    list_filter = ('teacher', LessonFilter, FreeFilter)
    inlines = (ClassInline,)
    fieldsets = (
        ('Planned lesson', {
            'fields': ('date', 'students'),
        }),
        ('Lesson', {
            'fields': ('teacher', 'lesson'),
        }),
    )
    ordering = ('-start',)

    def duration(self, instance):
        d = str(instance.end - instance.start).split(':')

        if len(d[0]) < 2:
            d[0] = '0%s' % d[0]

        return '%s:%s' % (d[0], d[1])

    def date(self, instance):
        return capfirst(naturalday(instance.start)) + ', ' + instance.start.strftime('%H:%m')

    def lesson(self, instance):
        return format_html('<a href = "%s">%s</a>' % (instance.lesson.admin_url, instance.lesson.internal_name))

    def lesson_name(self, instance):
        """
        Lesson name for dispaying in list
        """
        return instance.lesson.internal_name

    def students(self, instance):
        return "%s/%s" % (instance.taken_slots, instance.slots)

    def has_add_permission(self, request):
        """
        We don't allow to add new timeline entries via admin interface. One can
        use :view:`timeline.calendar`.
        """
        return False
