from django.contrib import admin
from .models import OrdinaryLesson, LessonWithNative, Product1


# Register your models here.


@admin.register(OrdinaryLesson)
class OrdinaryLessonAdmin(admin.ModelAdmin):
    list_display = ('internal_name', 'duration')


@admin.register(LessonWithNative)
class LessonWithNativeAdmin(admin.ModelAdmin):
    list_display = ('internal_name', 'duration')


@admin.register(Product1)
class Product1Admin(admin.ModelAdmin):
    pass
