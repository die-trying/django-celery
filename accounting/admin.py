from date_range_filter import DateRangeFilter
from django.contrib import admin

from accounting.models import Event as AccEvent
from elk.admin import ModelAdmin


@admin.register(AccEvent)
class AccountingEventAdmin(ModelAdmin):
    list_display = ('time', 'teacher', 'customers', 'event_type')
    list_filter = (
        ('timestamp', DateRangeFilter),
        ('teacher', admin.RelatedOnlyFieldListFilter),
        'event_type',
    )
    readonly_fields = ('time', 'teacher', 'event_type', 'customers')
    exclude = ('originator_id', 'originator_type')

    def has_add_permission(self, *args):
        return False

    def has_delete_permission(self, *args):
        return False

    def time(self, instance):
        return self._datetime(instance.originator_time)

    def customers(self, instance):
        return ', '.join(map(str, instance.originator_customers))
