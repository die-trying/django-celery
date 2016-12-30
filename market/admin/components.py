from django.utils import timezone

from elk.admin import ModelAdmin, TabularInline
from elk.admin.filters import BooleanFilter
from market.models import Class, Subscription


class IsFinishedFilter(BooleanFilter):
    title = 'Is fully used'
    parameter_name = 'is_fully_used'

    def t(self, request, queryset):
        return queryset.filter(is_fully_used=True)

    def f(self, request, queryset):
        return queryset.filter(is_fully_used=False)


class ProductContainerAdmin(ModelAdmin):
    ordering = ['-buy_date']

    def purchase_date(self, instance):
        return self._datetime(instance.buy_date)

    purchase_date.admin_order_field = 'buy_date'

    def available(self, instance):
        return not instance.is_fully_used

    available.boolean = True
    available.admin_order_field = '-is_fully_used'


class SubscriptionsInline(TabularInline):
    model = Subscription
    readonly_fields = ('product', 'when', 'is_fully_used')
    fieldsets = (
        (None, {
            'fields': ('product', 'when', 'is_fully_used')
        }),
    )

    def product(self, instance):
        return str(instance.product)

    def when(self, instance):
        return self._datetime(instance.buy_date)

    def has_add_permission(self, instance):
        return False

    def has_delete_permission(self, request, instance):
        return False


class ClassesInline(TabularInline):
    model = Class
    verbose_name = 'Purchased lesson'
    verbose_name_plural = 'Purchased lessons'
    readonly_fields = ['lesson_type', 'teacher', 'scheduled_time']
    fieldsets = (
        (None, {
            'fields': ('lesson_type', 'teacher', 'scheduled_time')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('timeline__start')

    def has_add_permission(self, request):
        """
        Administration of the classes is made on the separate page for harnessin
        the `GeneralStackedInline`
        """
        return False

    def has_delete_permission(self, request, instance):
        return False

    def scheduled_time(self, instance):
        if instance.timeline is not None:
            return self._datetime(instance.timeline.start)
        else:
            return '—'

    def teacher(self, instance):
        if instance.timeline is not None:
            return str(instance.timeline.teacher)
        else:
            return '—'
