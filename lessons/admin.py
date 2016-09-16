from django.contrib import admin

from elk.admin import ModelAdmin

from .models import HappyHour, LessonWithNative, MasterClass, OrdinaryLesson, PairedLesson


class LessonAdmin(ModelAdmin):
    """
    Abstract admin for the lessons.
    """
    list_display = ['__str__', 'duration']
    list_filter = []

    def __init__(self, *args, **kwargs):
        """
        Add host display for hosted lessons
        """
        super().__init__(*args, **kwargs)

@admin.register(OrdinaryLesson)
class OrdinaryLessonAdmin(LessonAdmin):
    pass


@admin.register(LessonWithNative)
class LessonWithNativeAdmin(LessonAdmin):
    pass


@admin.register(PairedLesson)
class PairedLessonAdmin(LessonAdmin):
    pass


@admin.register(HappyHour)
class HappyHourAdmin(LessonAdmin):
    pass


@admin.register(MasterClass)
class MasterClassAdmin(LessonAdmin):
    pass
