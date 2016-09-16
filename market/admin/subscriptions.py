from date_range_filter import DateRangeFilter
from django.contrib import admin

from elk.admin import BooleanFilter
from market.admin.components import BuyableModelAdmin, ClassesLeftInline, ClassesPassedInline
from market.models import Subscription


class IsFinishedFilter(BooleanFilter):
    title = 'Is fully used'
    parameter_name = 'is_fully_used'

    def t(self, request, queryset):
        return queryset.filter(is_fully_used=True)

    def f(self, request, queryset):
        return queryset.filer(is_fully_used=False)


@admin.register(Subscription)
class SubscriptionAdmin(BuyableModelAdmin):
    list_display = ('customer', '__str__', 'lesson_usage', 'planned_lessons', 'purchase_date',)
    list_filter = (('buy_date', DateRangeFilter), IsFinishedFilter)
    readonly_fields = ('lesson_usage', 'purchase_date', 'planned_lessons')
    inlines = (ClassesLeftInline, ClassesPassedInline)
    search_fields = ('customer__user__first_name', 'customer__user__last_name')
    fieldsets = (
        (None, {
            'fields': ('purchase_date', 'lesson_usage', 'customer', 'buy_price', 'product_type',)
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

    def has_delete_permission(self, request, obj=None):
        if obj and (obj.classes.filter(is_fully_used=True) or obj.classes.filter(timeline__isnull=False)):
            return False
        return True
