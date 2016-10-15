from django.template import Context, Template
from django.test import override_settings
from moneyed import RUB, Money

from elk.utils.testing import TestCase, create_customer
from payments.templatetags import stripe
from products.models import Product1


class TestPaymentFormTag(TestCase):
    fixtures = ('products', 'lessons')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = Product1.objects.get(pk=1)
        cls.customer = create_customer()
        cls.cost = Money(30, RUB)

    @override_settings(STRIPE_PK='test_100500_pk')
    def test_context(self):
        ctx = stripe._ctx(self.product, self.cost, self.customer)

        self.assertDictEqual(ctx, {
            'product': self.product,
            'crm': self.customer,
            'amount': 3000,
            'currency': 'RUB',
            'stripe_pk': 'test_100500_pk',
        })

    @override_settings(STRIPE_PK='test_100500_pk')
    def test_render(self):
        tpl = Template("{% load stripe_form from stripe %} {% stripe_form product cost customer %}")
        html = tpl.render(Context({
            'product': self.product,
            'cost': self.cost,
            'customer': self.customer,
        }))

        self.assertIn('data-key="test_100500_pk"', html)
        self.assertIn('data-email="%s"' % self.customer.user.email, html)
