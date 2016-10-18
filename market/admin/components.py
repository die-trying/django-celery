from django.utils import timezone

from elk.admin import ModelAdmin, TabularInline
from market.models import Class, Subscription


class ProductContainerAdmin(ModelAdmin):
    ordering = ['-buy_date']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(active=1)

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


class ClassesInlineBase(TabularInline):
    model = Class

    def has_add_permission(self, request):
        """
        Administration of the classes is made on the separate page for harnessin
        the `GeneralStackedInline`
        """
        return False

    def has_delete_permission(self, request, instance):
        return False

    def buy_time(self, instance):
        return self._datetime(instance.buy_date)


class ClassesLeftInline(ClassesInlineBase):
    verbose_name = 'Purchased lesson'
    verbose_name_plural = 'Purchased lessons left'
    readonly_fields = ('lesson_type', 'source', 'buy_time')
    fieldsets = (
        (None, {
            'fields': ('lesson_type', 'source', 'buy_time')
        }),
    )

    def source(self, instance):
        if not instance.subscription:
            return '—'
        else:
            return str(instance.subscription.product)

    def buy_time(self, instance):
        if not instance.subscription:
            return super().buy_time(instance)
        return '—'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(is_fully_used=True)


class ClassesPassedInline(ClassesInlineBase):
    verbose_name = 'Lesson'
    verbose_name_plural = 'Passed classes'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(timeline__start__lt=timezone.now())  # TODO: replace it with .is_full_used property

    readonly_fields = ('lesson', 'teacher')
    fieldsets = (
        (None, {
            'fields': ('lesson', 'teacher')
        }),
    )

    def lesson(self, instance):
        """
        Display actual lesson name for hosted lessons
        """
        if not hasattr(instance.timeline.lesson, 'host'):
            return instance.lesson
        else:
            return instance.timeline.lesson.name

    def teacher(self, instance):
        return instance.timeline.teacher.user.crm.full_name
