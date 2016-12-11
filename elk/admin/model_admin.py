from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.template.defaultfilters import capfirst, time
from django.utils import timezone
from django.utils.html import format_html
from django_markdown.models import MarkdownField
from django_markdown.widgets import AdminMarkdownWidget
from image_cropping import ImageCroppingMixin
from suit.widgets import SuitSplitDateTimeWidget

from elk.admin.widgets import ForeignKeyWidget


class AdminHelpersMixin():
    def _email(self, email):
        return format_html(
            '<a href="mailto:%s">%s</a>' % (email, email)
        )

    def _datetime(self, date):
        local = timezone.localtime(date)
        return capfirst(naturalday(local)) + ' ' + self._time(local)

    def _time(self, date):
        return time(date, 'TIME_FORMAT')


class ModelAdmin(ImageCroppingMixin, admin.ModelAdmin, AdminHelpersMixin):
    """
    Abstract base class for all admin modules. Currently, supports only a minor
    set of helpers
    """
    formfield_overrides = {
        MarkdownField: {'widget': AdminMarkdownWidget},
        models.DateTimeField: {'widget': SuitSplitDateTimeWidget},
        models.ForeignKey: {'widget': ForeignKeyWidget},
    }

    class Media:
        js = [
            '/admin/jsi18n/',  # django-suit forgets to include this script

            'admin/js/calendar.js',
            'admin/js/admin/DateTimeShortcuts.js',  # let calendar js work on all pages, not only on details
        ]


class TabularInline(admin.TabularInline, AdminHelpersMixin):
    pass


class StackedInline(admin.StackedInline, AdminHelpersMixin):
    pass
