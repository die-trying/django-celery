from django.contrib import admin

from .models import Entry as TimelineEntry

# Register your models here.


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    exclude = ('customers', 'event_id')
    list_display = ('__str__', 'is_free')
    pass
