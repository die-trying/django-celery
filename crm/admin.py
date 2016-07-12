from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as StockUserAdmin
from django.contrib.auth.models import User

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
    list_display = ('full_name', 'country', 'bought_classes', 'bought_subscriptions', 'email', 'date_arrived', 'source')
    list_filter = ('country', 'current_level',)
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

    def get_queryset(self, request):
        """
        In this module we see only registered students. One should edit
        potential customers via the 'Users' page.
        """
        queryset = super(admin.ModelAdmin, self).get_queryset(request)
        return queryset.filter(user__isnull=False)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
