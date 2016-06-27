from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as StockUserAdmin
from django.contrib.auth.models import User

from .models import Customer

# Register your models here.


# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ('customer_name', 'country', 'email', 'date_arrived')
#
#     def customer_name(self, obj):
#         return str(obj)

class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(StockUserAdmin):
    inlines = (CustomerInline, )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'country', 'email', 'date_arrived')
