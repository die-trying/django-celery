from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as StockUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _

from elk.utils.admin import BooleanFilter, ModelAdmin, TabularInline
from hub.models import Class

from .models import Customer, RegisteredCustomer


# Register your models here.


class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    exclude = ('customer_email', 'customer_first_name', 'customer_last_name')
    verbose_name = 'CRM Profile'

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(StockUserAdmin):
    inlines = (CustomerInline, )
    fieldsets = (
        ('Personal info', {
            'fields': ('username', 'password', 'first_name', 'last_name', 'email', 'is_active', 'is_staff')
        }),
    )


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    """
    This admin module is for managing CRM-only customer databases
    e.g. potential customers.
    """
    list_display = ('full_name', 'country', 'email', 'source', 'date_arrived')

    def get_queryset(self, request):
        """
        Disable administration of customers, assigned to users.
        One should edit this customer via the 'Users' page.
        """
        queryset = super().get_queryset(request)
        return queryset.filter(user=None)


class HasClassesFilter(BooleanFilter):
    title = _('Has classes')
    parameter_name = 'has_classes'

    def t(self, request, queryset):
        return queryset.filter(classes__isnull=False).distinct('pk')

    def n(self, request, queryset):
        return queryset.filter(classes__isnull=True)


class HasSubscriptionsFilter(BooleanFilter):
    title = _('Has subscriptions')
    parameter_name = 'has_subscriptions'

    def t(self, request, queryset):
        return queryset.filter(subscriptions__isnull=False).distinct('pk')

    def n(self, request, queryset):
        return queryset.filter(subscriptions__isnull=True)


class ClassesInlineBase(TabularInline):
    model = Class

    def when(self, instance):
        return self._datetime(instance.buy_date) + ' ' + self._time(instance.buy_date)

    def has_add_permission(self, request):
        """
        Administration of the classes is made on the separate page for harnessin
        the `GeneralStackedInline`
        """
        return False


class ClassesLeftInline(ClassesInlineBase):
    verbose_name = 'Bought lesson'
    verbose_name_plural = 'Bought lessons left'
    readonly_fields = ('lesson', 'when', 'buy_source')
    fieldsets = (
        (None, {
            'fields': ('lesson', 'when', 'buy_source')
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(timeline__start__lt=timezone.now())


class ClassesPassedInline(ClassesInlineBase):
    verbose_name = 'Lesson'
    verbose_name_plural = 'Passed classes'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(timeline__start__lt=timezone.now())

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

    def has_delete_permission(self, request, instance):
        """
        For obvious reasons passed class should not be deletable event through admin
        """
        return False


@admin.register(RegisteredCustomer)
class ExistingCustomerAdmin(ModelAdmin):
    """
    The admin module for manager current customers without managing users
    """
    list_display = ('full_name', 'classes', 'subscriptions', 'country', 'date_arrived')
    list_filter = (HasClassesFilter, HasSubscriptionsFilter,)
    actions = None
    readonly_fields = ('__str__', 'email', 'student', 'user', 'arrived', 'classes', 'subscriptions')
    inlines = (ClassesLeftInline, ClassesPassedInline)
    fieldsets = (
        (None, {
            'fields': ('student', 'email', 'arrived', 'classes', 'subscriptions')
        }),
        ('Profile', {
            'fields': ('birthday', 'country', 'native_language', 'profile_photo', 'starting_level', 'current_level')
        }),
        ('Social', {
            'fields': ('skype', 'facebook', 'instagram', 'twitter', 'linkedin')
        }),
    )

    def classes(self, instance):
        total = instance.classes.all()
        if not total:
            return '—'

        finished = total.filter(timeline__start__lte=timezone.now())
        return '%d/%d' % (finished.count(), total.count())

    def subscriptions(self, instance):
        if not instance.classes:
            return '—'

        total = instance.classes.distinct('subscription').values_list('subscription', flat=True)

        if not total:
            return '—'

        finished = Class.objects.filter(subscription_id__in=total).exclude(is_scheduled=False).filter(timeline__start__gt=timezone.now()).distinct('subscription').values_list('subscription', flat=True)
        return '%d/%d' % (finished.count(), total.count())

    def email(self, instance):
        return self._email(instance.email)

    def arrived(self, instance):
        return self._datetime(instance.date_arrived) + ', ' + instance.source

    def student(self, instance):
        return "%s (%s)" % (instance.__str__(), instance.user.username)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
