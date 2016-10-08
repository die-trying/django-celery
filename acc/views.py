from django.views.generic.base import TemplateView

from products.models import Product1, SimpleSubscription


class Homepage(TemplateView):
    template_name = 'acc/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['product1'] = Product1.objects.get(pk=1)
        ctx['simple_subscription'] = SimpleSubscription.objects.get(pk=1)

        return ctx
