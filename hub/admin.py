from django.contrib import admin

from elk.utils.admin import BooleanFilter, ModelAdmin
from hub.admin.components import ClassesLeftInline, ClassesPassedInline
from hub.models import Subscription


class IsFinishedFilter(BooleanFilter):
    title = 'Is fully used'
    parameter_name = 'is_fully_used'

    def t(self, request, queryset):
        return queryset.filter(is_fully_used=True)

    def f(self, request, queryset):
        return queryset.filer(is_fully_used=False)


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ('customer', '__str__', 'lesson_usage', 'planned_lessons', 'buy_time', 'buy_price')
    list_filter = (IsFinishedFilter,)
    readonly_fields = ('lesson_usage', 'buy_time', 'planned_lessons')
    actions = None
    inlines = (ClassesLeftInline, ClassesPassedInline)
    search_fields = ('customer__user__first_name', 'customer__user__last_name')
    fieldsets = (
        (None, {
            'fields': ('customer', 'buy_price', 'product_type')
        }),
    )

    def lesson_usage(self, instance):
        total = instance.classes
        finished = total.filter(is_fully_used=True)

        return '%d/%d' % (finished.count(), total.count())

    def planned_lessons(self, instance):
        """
        Lessons, that are planned, but not finished yet
        """
        scheduled = instance.classes.exclude(is_fully_used=True) \
            .filter(timeline__isnull=False).count()

        if not scheduled:
            return '—'
        else:
            return scheduled

    def buy_time(self, instance):
        return self._datetime(instance.buy_date) + ' ' + self._time(instance.buy_date)

    def has_delete_permission(self, request, obj=None):
        if obj and (obj.classes.filter(is_fully_used=True) or obj.classes.filter(timeline__isnull=False)):
            return False
        return True
