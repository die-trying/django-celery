from django.contrib import admin

from .models import Product1


# Register your models here.

@admin.register(Product1)
class Product1Admin(admin.ModelAdmin):
    pass
