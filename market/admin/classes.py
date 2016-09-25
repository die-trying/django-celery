from date_range_filter import DateRangeFilter
from django.contrib import admin

from elk.admin.filters import BooleanFilter
from market.admin.actions import MarkAsUsedForm, mark_as_used, renew
from market.admin.components import BuyableModelAdmin
from market.models import Class


class BuySubscriptionFilter(BooleanFilter):
    title = "Single purchase"
    parameter_name = "single_purchased"

    def t(self, request, queryset):
        return queryset.filter(subscription__isnull=True)

    def f(self, request, queryset):
        return queryset.filter(subscription__isnull=False)


class AvailableFilter(BooleanFilter):
    title = "Available"
    parameter_name = "is_available"

    def t(self, request, queryset):
        return queryset.filter(is_fully_used=False)

    def f(self, request, queryset):
        return queryset.filter(is_fully_used=True)


@admin.register(Class)
class ClassAdmin(BuyableModelAdmin):
    verbose_name = 'Class'
    verbose_name_plural = 'Purchased lessons'
    model = Class
    list_display = ('lesson_type', 'customer', 'available', 'purchase_date')
    list_filter = (('buy_date', DateRangeFilter), BuySubscriptionFilter,)
    search_fields = ('customer__user__first_name', 'customer__user__last_name')
    actions = [mark_as_used, renew]
    action_form = MarkAsUsedForm
    actions_on_top = False
    actions_on_bottom = True

    fieldsets = (
        (None, {
            'fields': ('customer', 'buy_price', 'lesson_type')
        }),
    )
