from django.contrib import admin
from django.utils.translation import ugettext as _

from crm.models import Customer
from elk.admin import BooleanFilter, ModelAdmin
from market.admin.components import ClassesLeftInline, ClassesPassedInline, SubscriptionsInline
from market.models import Subscription


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


@admin.register(Customer)
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
        ('Attribution', {
            'fields': ('responsible',)
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

        finished = Subscription.objects.filter(pk__in=total, is_fully_used=True)
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
