"""
Abstract admin classes. All your ModelAdmins should be subclasses from this Modeladmin
"""
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturalday
from django.template.defaultfilters import capfirst, time
from django.utils.html import format_html
from django_markdown.models import MarkdownField
from django_markdown.widgets import AdminMarkdownWidget

admin.site.disable_action('delete_selected')  # disable delete selected action site-wide


class BooleanFilter(admin.SimpleListFilter):
    """
    Abstract base class for simple boolean filter in admin. You should define only
    `title`, unique `parameter_name` and two methods: `t` and `f`, returning a queryset
    when filter is set to True and False respectively:

        class HasClassesFilter(BooleanFilter):
            title = _('Has classes')
            parameter_name = 'has_classes'

            def t(self, request, queryset):
                return queryset.filter(classes__isnull=False).distinct('pk')

            def n(self, request, queryset):
                return queryset.filter(classes__isnull=True)

    """
    def lookups(self, request, model_admin):
        return (
            ('t', 'Yes'),
            ('f', 'No'),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            if self.value() == 't':
                return self.t(request, queryset)
            else:
                return self.f(request, queryset)


class AdminHelpersMixin():
    def _email(self, email):
        return format_html(
            '<a href="mailto:%s">%s</a>' % (email, email)
        )

    def _datetime(self, date):
        return capfirst(naturalday(date))

    def _time(self, date):
        return time(date, 'SHORT_TIME_FORMAT')


class ModelAdmin(admin.ModelAdmin, AdminHelpersMixin):
    """
    Abstract base class for all admin modules. Currently, supports only a minor
    set of helpers
    """
    formfield_overrides = {MarkdownField: {'widget': AdminMarkdownWidget}}

    class Media:
        js = ('/admin/jsi18n/',)  # django-suit forgets to include this script


class TabularInline(admin.TabularInline, AdminHelpersMixin):
    pass


class StackedInline(admin.StackedInline, AdminHelpersMixin):
    pass


def write_log_entry(request, object, action_flag=admin.models.CHANGE, change_message='Changed'):
    entry = admin.models.LogEntry(
        user=request.user,
        object_id=object.pk,
        content_type=ContentType.objects.get_for_model(object),  # move it away from this function if you experience problems
        object_repr=str(object),
        action_flag=action_flag,
        change_message=change_message,
    )
    entry.save()
