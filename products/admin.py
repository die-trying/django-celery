from django.contrib import admin

from elk.admin import ModelAdmin
from products.models import Product1, SimpleSubscription


@admin.register(Product1)
class Product1Admin(ModelAdmin):
    readonly_fields = Product1.LESSONS  # don't allow direct adding lessons to product. Please use migrations

    def has_add_permission(self, request):
        return False


@admin.register(SimpleSubscription)
class SimpleSubscriptionAdmin(ModelAdmin):
    readonly_fields = SimpleSubscription.LESSONS  # don't allow direct adding lessons to product. Please use migrations

    def has_add_permission(self, request):
        return False
