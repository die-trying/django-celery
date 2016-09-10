from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as StockUserAdmin
from django.contrib.auth.models import User

from crm.models import Customer
from elk.admin import StackedInline


class CustomerInline(StackedInline):
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
