from django.utils import timezone

from elk.admin import ModelAdmin, TabularInline, write_log_entry
from hub.models import Class, Subscription


class BuyableProductModelAdmin(ModelAdmin):
    actions = None

    def get_queryset(self, request):
        return super().get_queryset(request).filter(active=1)

    def buy_time(self, instance):
        return self._datetime(instance.buy_date) + ' ' + self._time(instance.buy_date)

    def available(self, instance):
        return not instance.is_fully_used

    available.boolean = True


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
        return self._datetime(instance.buy_date) + ' ' + self._time(instance.buy_date)

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
        return self._datetime(instance.buy_date) + ' ' + self._time(instance.buy_date)


class ClassesLeftInline(ClassesInlineBase):
    verbose_name = 'Bought lesson'
    verbose_name_plural = 'Bought lessons left'
    readonly_fields = ('lesson', 'source', 'buy_time')
    fieldsets = (
        (None, {
            'fields': ('lesson', 'source', 'buy_time')
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

    readonly_fields = ('lesson', 'teacher', 'when',)
    fieldsets = (
        (None, {
            'fields': ('lesson', 'teacher', 'when')
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

    def when(self, instance):
        return self._datetime(instance.timeline.start) + ' ' + self._time(instance.timeline.start)


def mark_as_used(modeladmin, request, queryset):
    """
    Admin action to mark classes as fully used
    """
    for c in queryset.all():
        if not c.is_fully_used:
            c.mark_as_fully_used()
            write_log_entry(
                request=request,
                object=c,
                change_message='Marked as used',
            )


def renew(modeladmin, request, queryset):
    """
    Admin action to mark classes as renewed
    """
    for c in queryset.all():
        if c.is_fully_used:
            c.renew()
            write_log_entry(
                request=request,
                object=c,
                change_message='Renewed',
            )
