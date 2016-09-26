from django.contrib import admin
from django.utils.translation import ugettext as _

from crm.models import Customer, CustomerNote
from elk.admin import ModelAdmin, StackedInline
from elk.admin.filters import BooleanFilter
from market.admin.components import ClassesLeftInline, ClassesPassedInline, SubscriptionsInline
from market.models import Subscription


class HasClassesFilter(BooleanFilter):
    title = _('Has classes')
    parameter_name = 'has_classes'

    def t(self, request, queryset):
        return queryset.filter(classes__isnull=False).distinct('pk')

    def n(self, request, queryset):
        return queryset.filter(classes__isnull=True)


class HasSubscriptionsFilter(BooleanFilter):
    title = _('Has subscriptions')
    parameter_name = 'has_subscriptions'

    def t(self, request, queryset):
        return queryset.filter(subscriptions__isnull=False).distinct('pk')

    def n(self, request, queryset):
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


@admin.register(Customer)
class ExistingCustomerAdmin(ModelAdmin):
    """
    The admin module for manager current customers without managing users
    """
    list_display = ('full_name', 'country', 'Languages', 'curator', 'classes', 'subscriptions', 'date_arrived')
    list_filter = (
        CountryFilter,
        ('curator', admin.RelatedOnlyFieldListFilter),
        ('company', admin.RelatedOnlyFieldListFilter),
        ('languages', admin.RelatedOnlyFieldListFilter),
        HasClassesFilter,
        HasSubscriptionsFilter
    )
    actions = None
    readonly_fields = ('__str__', 'email', 'student', 'user', 'arrived', 'classes', 'subscriptions', 'corporate')
    search_fields = ('user__first_name', 'user__last_name')
    inlines = (CustomerNotesInline, SubscriptionsInline, ClassesLeftInline, ClassesPassedInline)
    fieldsets = (
        (None, {
            'fields': ('student', 'email', 'arrived', 'classes', 'subscriptions', 'corporate')
        }),
        ('Attribution', {
            'fields': ('curator', 'company', 'languages'),
        }),
        ('Profile', {
            'fields': ('country', 'timezone', 'birthday', 'native_language', 'profile_photo', 'starting_level', 'current_level')
        }),
        ('Social', {
            'fields': ('skype', 'facebook', 'instagram', 'twitter', 'linkedin')
        }),
    )

    def Languages(self, instance):
        if not instance.languages.count():
            return '-'

        return ', '.join(instance.languages.all().values_list('name', flat=True))

    def classes(self, instance):
        total = instance.classes.all()
        if not total:
            return '—'

        finished = total.filter(is_fully_used=True)
        return '%d/%d' % (finished.count(), total.count())

    def subscriptions(self, instance):
        if not instance.classes:
            return '—'

        total = instance.classes.distinct('subscription').values_list('subscription', flat=True)

        if not total:
            return '—'

        finished = Subscription.objects.filter(pk__in=total, is_fully_used=True)
        return '%d/%d' % (finished.count(), total.count())

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

    def arrived(self, instance):
        return self._datetime(instance.date_arrived) + ', ' + instance.source

    def student(self, instance):
        return "%s (%s)" % (instance.__str__(), instance.user.username)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
