from django.contrib import admin

from .models import Customer

# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'country', 'email', 'date_arrived')

    def customer_name(self, obj):
        return str(obj)
