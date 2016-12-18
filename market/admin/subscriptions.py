from date_range_filter import DateRangeFilter
from django.contrib import admin
from django.db.models import F
from django.utils import timezone

from elk.admin.filters import BooleanFilter
from market.admin.actions import export_emails
from market.admin.components import ClassesLeftInline, ClassesPassedInline, IsFinishedFilter, ProductContainerAdmin
from market.models import Subscription


class IsDueFilter(BooleanFilter):
    title = 'Is due'
    parameter_name = 'is_due'

    def t(self, request, queryset):
        return queryset.filter(buy_date__lte=timezone.now() - F('duration'))

    def f(self, request, queryset):
        return queryset.filter(buy_date__gt=timezone.now() - F('duration'))


@admin.register(Subscription)
class SubscriptionAdmin(ProductContainerAdmin):
    list_display = ('customer', '__str__', 'lesson_usage', 'planned_lessons', 'purchase_date', 'not_due')
    list_filter = (IsFinishedFilter, IsDueFilter, ('buy_date', DateRangeFilter))
    readonly_fields = ('lesson_usage', 'purchase_date', 'planned_lessons')
    inlines = (ClassesLeftInline, ClassesPassedInline)
    search_fields = ('customer__user__first_name', 'customer__user__last_name')
    actions = [export_emails]
    actions_on_top = False
    actions_on_bottom = True
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

    def not_due(self, instance):
        return not instance.is_due()  # it's better displayed when reverse

    not_due.boolean = True
