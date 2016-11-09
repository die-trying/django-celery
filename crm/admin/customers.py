from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from crm.models import Customer, CustomerNote
from elk.admin import ModelAdmin, StackedInline
from elk.admin.filters import BooleanFilter
from elk.templatetags.skype import skype_chat
from market.admin.components import ClassesLeftInline, ClassesPassedInline, SubscriptionsInline


class HasClassesFilter(BooleanFilter):
    title = _('Has classes')
    parameter_name = 'has_classes'

    def t(self, request, queryset):
        return queryset.filter(classes__isnull=False).distinct('pk')

    def f(self, request, queryset):
        return queryset.filter(classes__isnull=True)


class HasSubscriptionsFilter(BooleanFilter):
    title = _('Has subscriptions')
    parameter_name = 'has_subscriptions'

    def t(self, request, queryset):
        return queryset.filter(subscriptions__isnull=False).distinct('pk')

    def f(self, request, queryset):
        return queryset.filter(subscriptions__isnull=True)


class CountryFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        return (
            [str(i.country), i.country.name] for i in Customer.objects.distinct('country')
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        return queryset.filter(country=self.value())


class CustomerNotesInline(StackedInline):
    model = CustomerNote
    can_delete = False
    extra = 1
    template = 'crm/admin/customer_notes.html'
    fieldsets = (
        (None, {
            'fields': ('text',)
        }),
    )

    def has_change_permission(self, request, obj=None):
        return False


def export_to_mailchimp(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    return redirect('crm:mailchimp_csv', ids=','.join(selected))


@admin.register(Customer)
class ExistingCustomerAdmin(ModelAdmin):
    """
    The admin module for manager current customers without managing users
    """
    list_display = ('full_name', 'country', 'Languages', 'curator', 'classes', 'subscriptions', '_skype', 'date_arrived')
    list_filter = (
        CountryFilter,
        ('curator', admin.RelatedOnlyFieldListFilter),
        ('company', admin.RelatedOnlyFieldListFilter),
        ('languages', admin.RelatedOnlyFieldListFilter),
        HasClassesFilter,
        HasSubscriptionsFilter
    )
    actions = [export_to_mailchimp]
    readonly_fields = ('__str__', 'email', 'student', 'user', 'arrived', 'classes', 'subscriptions', 'corporate')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    inlines = (CustomerNotesInline, SubscriptionsInline, ClassesLeftInline, ClassesPassedInline)
    fieldsets = (
        (None, {
            'fields': ('student', 'email', 'arrived', 'classes', 'subscriptions', 'corporate')
        }),
        ('Attribution', {
            'fields': ('curator', 'company', 'languages'),
        }),
        ('Profile', {
            'fields': ('profile_photo', 'profile_photo_cropping', 'country', 'timezone', 'birthday', 'native_language', 'starting_level', 'current_level')
        }),
        ('Contacts', {
            'fields': ('phone', 'skype', 'facebook', 'instagram', 'twitter', 'linkedin')
        }),
    )

    def get_queryset(self, request):
        """
        Hide teacher profiles from the grid, show only when teacher card requested
        """
        queryset = super().get_queryset(request)

        if request.resolver_match is not None and request.resolver_match.url_name == 'crm_customer_change':
            return queryset

        return queryset.prefetch_related('subscriptions', 'classes', 'user').filter(user__teacher_data__isnull=True)

    def Languages(self, instance):
        if not instance.languages.count():
            return '-'

        return ', '.join(instance.languages.values_list('name', flat=True))

    def classes(self, instance):
        total = instance.classes.count()
        if not total:
            return '—'

        finished = instance.classes.filter(is_fully_used=True).count()
        return '%d/%d' % (finished, total)

    def subscriptions(self, instance):
        if not instance.classes.count():
            return '—'

        total = instance.subscriptions.count()

        if not total:
            return '—'

        finished = instance.subscriptions.filter(is_fully_used=True).count()
        return '%d/%d' % (finished, total)

    def save_formset(self, request, form, formset, change):
        """
        Save customer note author
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, CustomerNote):
                instance.teacher = request.user.teacher_data

        super().save_formset(request, form, formset, change)

    def corporate(self, instance):
        if instance.company is not None:
            return _('True')
        return _('False')

    def email(self, instance):
        return self._email(instance.email)

    def _skype(self, instance):
        if instance.skype:
            return format_html(skype_chat(instance))
        else:
            return '—'

    _skype.admin_order_field = 'skype'

    def arrived(self, instance):
        return self._datetime(instance.date_arrived) + ', ' + instance.source

    def student(self, instance):
        return "%s (%s)" % (instance.__str__(), instance.user.username)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
