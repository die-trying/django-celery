from date_range_filter import DateRangeFilter
from django.contrib import admin

from accounting.models import Event as AccEvent
from elk.admin import ModelAdmin


@admin.register(AccEvent)
class AccountingEventAdmin(ModelAdmin):
    list_display = ('teacher', 'event_type', 'time')
    list_filter = (
        ('timestamp', DateRangeFilter),
        ('teacher', admin.RelatedOnlyFieldListFilter),
        'event_type',
    )
    readonly_fields = ('time', 'teacher', 'event_type')
    exclude = ('originator_id', 'originator_type')

    def has_add_permission(self, *args):
        return False

    def time(self, instance):
        return self._datetime(instance.timestamp)
