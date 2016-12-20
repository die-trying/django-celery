from django.contrib import admin

from elk.admin.filters import BooleanFilter
from market.admin.actions import MarkAsUsedForm, mark_as_used, renew
from market.admin.components import IsFinishedFilter, ProductContainerAdmin
from market.models import Class


class BuySubscriptionFilter(BooleanFilter):
    title = "Single purchase"
    parameter_name = "single_purchased"

    def t(self, request, queryset):
        return queryset.filter(subscription__isnull=True)

    def f(self, request, queryset):
        return queryset.filter(subscription__isnull=False)


@admin.register(Class)
class ClassAdmin(ProductContainerAdmin):
    verbose_name = 'Class'
    verbose_name_plural = 'Purchased lessons'
    model = Class
    list_display = ('lesson_type', 'customer', 'available', 'purchase_date')
    list_filter = (BuySubscriptionFilter, IsFinishedFilter)
    search_fields = ('customer__user__first_name', 'customer__user__last_name')
    actions = [mark_as_used, renew]
    action_form = MarkAsUsedForm
    actions_on_top = False
    actions_on_bottom = True
    fieldsets = (
        (None, {
            'fields': ('customer', 'buy_price', 'lesson_type', 'teacher')
        }),
    )
    list_select_related = True

    def teacher(self, instance):
        if not self.available(instance):
            return instance.timeline.teacher
        else:
            return '—'

    def get_readonly_fields(self, request, instance=None):
        """
        Restrict editing:
            — classes by subscription can't change customer and buy_price
            — scheduled classes can't change lesson_type
        """
        readonly_fields = ['finish_date', 'teacher']

        if instance is not None:
            if not self.available(instance):
                readonly_fields += ['lesson_type']

            if instance.subscription is not None:
                readonly_fields += ['customer', 'buy_price']

        return readonly_fields
