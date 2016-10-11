from django.contrib import admin
from django.utils.translation import ugettext as _

from elk.admin import ModelAdmin
from products.models import Product1, SimpleSubscription, Tier


class CountryFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        return (
            [str(i.country), i.country.name] for i in Tier.objects.distinct('country')
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        return queryset.filter(country=self.value())


@admin.register(Product1)
class Product1Admin(ModelAdmin):
    readonly_fields = Product1.LESSONS  # don't allow direct adding lessons to product. Please use migrations

    def has_add_permission(self, request):
        return False


@admin.register(SimpleSubscription)
class SimpleSubscriptionAdmin(ModelAdmin):
    readonly_fields = SimpleSubscription.LESSONS  # don't allow direct adding lessons to product. Please use migrations

    def has_add_permission(self, request):
        return False


@admin.register(Tier)
class TierAdmin(ModelAdmin):
    list_filter = (
        CountryFilter,
        ('product_type'),
        ('is_default'),
    )
    list_display = ('_country', 'is_default', 'product', '_cost')
    exclude = ['product_id']

    def _country(self, instance):
        return instance.country.name

    _country.admin_order_field = 'country'

    def _cost(self, instance):
        return '%s %s' % (instance.cost.amount, instance.cost.currency)

    _cost.admin_order_field = 'cost'
