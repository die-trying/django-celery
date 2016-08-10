from django.contrib import admin

from elk.admin import BooleanFilter
from hub.admin.components import BuyableProductModelAdmin
from hub.models import Class


class BuySubscriptionFilter(BooleanFilter):
    title = "Single bought"
    parameter_name = "single_bought"

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
class ClassAdmin(BuyableProductModelAdmin):
    verbose_name = 'Class'
    verbose_name_plural = 'Bought classes'
    model = Class
    list_display = ('lesson_type', 'customer', 'buy_time', 'available')
    list_filter = (AvailableFilter, BuySubscriptionFilter,)
    search_fields = ('customer__user__first_name', 'customer__user__last_name')

    fieldsets = (
        (None, {
            'fields': ('customer', 'buy_price', 'lesson_type')
        }),
    )
