from django.contrib import admin

from accounting.models import Event as AccEvent
from elk.admin import ModelAdmin


@admin.register(AccEvent)
class AccountingEventAdmin(ModelAdmin):
    list_display = ('teacher', 'event_type', 'time')

    def has_add_permission(self, *args):
        return False

    def time(self, instance):
        return self._datetime(instance.timestamp)
