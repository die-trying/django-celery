from django.contrib import admin

from .models import Entry as TimelineEntry

# Register your models here.


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    exclude = ('customer', 'event_id', 'event_type')
    list_display = ('__str__', 'is_free')
    pass
