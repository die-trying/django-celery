from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as StockUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from elk.admin import BooleanFilter, ModelAdmin
from market.admin.components import ClassesLeftInline, ClassesPassedInline, SubscriptionsInline

from .models import Customer, RegisteredCustomer


# Register your models here.


class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    exclude = ('customer_email', 'customer_first_name', 'customer_last_name')
    verbose_name = 'CRM Profile'

    def has_add_permission(self, request):
        return False

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(StockUserAdmin):
    inlines = (CustomerInline, )
    fieldsets = (
        ('Personal info', {
            'fields': ('username', 'password', 'first_name', 'last_name', 'email', 'is_active', 'is_staff')
        }),
    )


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


@admin.register(RegisteredCustomer)
class ExistingCustomerAdmin(ModelAdmin):
    """
    The admin module for manager current customers without managing users
    """
    list_display = ('full_name', 'classes', 'subscriptions', 'country', 'date_arrived')
    list_filter = (HasClassesFilter, HasSubscriptionsFilter,)
    actions = None
    readonly_fields = ('__str__', 'email', 'student', 'user', 'arrived', 'classes', 'subscriptions')
    inlines = (SubscriptionsInline, ClassesLeftInline, ClassesPassedInline)
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

        finished = total.filter(is_fully_used=True)
        return '%d/%d' % (finished.count(), total.count())

    def subscriptions(self, instance):
        if not instance.classes:
            return '—'

        total = instance.classes.distinct('subscription').values_list('subscription', flat=True)

        if not total:
            return '—'

        finished = total.filter(is_fully_used=True)
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
