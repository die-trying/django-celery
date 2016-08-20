from django.contrib import admin

from elk.admin import ModelAdmin

from .models import Product1


@admin.register(Product1)
class Product1Admin(ModelAdmin):
    pass
