from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils.html import format_html


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


class ModelAdmin(admin.ModelAdmin):
    """
    Abstract base class for all admin modules. Currently, supports only a minor
    set of helpers
    """

    def _email(self, email):
        return format_html(
            '<a href="mailto:%s">%s</a>' % (email, email)
        )

    def _datetime(self, date):
        return naturalday(date)
