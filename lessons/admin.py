from django.contrib import admin

from elk.admin import ModelAdmin
from lessons import models


@admin.register(models.Language)
class LanguageAdmin(ModelAdmin):
    pass


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

        if hasattr(self.model, 'host'):
            if 'host' not in self.list_display:
                self.list_display.insert(0, 'host')

            if 'host' not in self.list_filter:
                self.list_filter.insert(0, 'host')


@admin.register(models.PairedLesson)
class PairedLessonAdmin(LessonAdmin):
    pass


@admin.register(models.HappyHour)
class HappyHourAdmin(LessonAdmin):
    pass


@admin.register(models.MasterClass)
class MasterClassAdmin(LessonAdmin):
    pass
