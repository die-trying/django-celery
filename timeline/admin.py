from django.contrib import admin

from .models import Entry as TimelineEntry


# Register your models here.


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    exclude = ('customers', 'event_id')
    readonly_fields = ('taken_slots', 'end')
    list_display = ('teacher', 'start', 'duration', 'is_free')

    def duration(self, instance):
        d = str(instance.end - instance.start).split(':')

        if len(d[0]) < 2:
            d[0] = '0%s' % d[0]

        return '%s:%s' % (d[0], d[1])
