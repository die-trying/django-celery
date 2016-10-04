from django.contrib import admin

from elk.admin import ModelAdmin
from lessons import models


@admin.register(models.Language)
class LanguageAdmin(ModelAdmin):
    pass


class HostedLessonAdmin(ModelAdmin):
    """
    Abstract admin for the lessons.
    """
    list_display = ('host', '__str__', 'duration')
    list_filter = (
        ('host', admin.RelatedOnlyFieldListFilter),
    )

    def get_queryset(self, request):
        """
        Hide lessons without host from administrators. Lessons without host are used
        for subscriptions.
        """
        return super().get_queryset(request).filter(host__isnull=False)


@admin.register(models.PairedLesson)
class PairedLessonAdmin(HostedLessonAdmin):
    pass


@admin.register(models.HappyHour)
class HappyHourAdmin(HostedLessonAdmin):
    pass


@admin.register(models.MasterClass)
class MasterClassAdmin(HostedLessonAdmin):
    pass
