from django.contrib import admin

from .models import Entry as TimelineEntry


# Register your models here.


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    exclude = ('customers', 'event_id')
    readonly_fields = ('taken_slots',)
    list_display = ('teacher', 'start_time', 'is_free')
    pass
