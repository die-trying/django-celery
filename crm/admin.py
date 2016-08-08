from django.contrib import admin
from django.utils import timezone
from django.contrib.auth.admin import UserAdmin as StockUserAdmin
from django.contrib.auth.models import User

from .models import Customer, RegisteredCustomer
from hub.models import Class

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
class CustomerAdmin(admin.ModelAdmin):
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
        queryset = super(admin.ModelAdmin, self).get_queryset(request)
        return queryset.filter(user=None)


@admin.register(RegisteredCustomer)
class ExistingCustomerAdmin(admin.ModelAdmin):
    """
    The admin module for manager current customers without managing users
    """
    list_display = ('full_name', 'classes', 'subscriptions', 'full_name', 'date_arrived')
    # list_filter = ('country',)
    actions = None
    readonly_fields = ('__str__', 'email', 'user', 'date_arrived', 'starting_level')
    fieldsets = (
        (None, {
            'fields': ('user', '__str__', 'email', 'date_arrived', 'starting_level')
        }),
        ('Profile', {
            'fields': ('birthday', 'country', 'native_language', 'profile_photo', 'current_level')
        }),
        ('Social', {
            'fields': ('skype', 'facebook', 'instagram', 'twitter', 'linkedin')
        }),
    )

    def classes(self, instance):
        total = instance.classes.all()
        finished = total.filter(timeline__start__lte=timezone.now())
        return '%d/%d' % (finished.count(), total.count())

    def subscriptions(self, instance):
        if not instance.classes:
            return '0/0'

        total = instance.classes.distinct('subscription').values_list('subscription', flat=True)

        if not total:
            return '0/0'

        finished = Class.objects.filter(subscription_id__in=total).exclude(is_scheduled=False).filter(timeline__start__gt=timezone.now()).distinct('subscription').values_list('subscription', flat=True)
        return '%d/%d' % (finished.count(), total.count())

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
