from django.contrib.contenttypes.models import ContentType
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
        cls.product_type = ContentType.objects.get_for_model(cls.product)
        cls.customer = create_customer()
        cls.cost = Money(31.5, RUB)

        cls.tpl = Template("{% load stripe_form from stripe %} {% stripe_form product cost customer %}")

    @override_settings(STRIPE_PK='test_100500_pk')
    def test_context(self):
        ctx = stripe._ctx(self.product, self.cost, self.customer)

        self.assertDictEqual(ctx, {
            'product': self.product,
            'product_type': self.product_type.pk,
            'crm': self.customer,
            'amount': '31.5',
            'stripe_amount': 3150,
            'currency': 'RUB',
            'stripe_pk': 'test_100500_pk',
        })

    def test_stripe_parameters(self):
        html = self.tpl.render(Context({
            'product': self.product,
            'cost': self.cost,
            'customer': self.customer,
        }))

        self.assertIn('data-email="%s"' % self.customer.user.email, html)

    def test_processing_parameters(self):
        html = self.tpl.render(Context({
            'product': self.product,
            'cost': self.cost,
            'customer': self.customer,
        }))

        self.assertIn('data-product-type="%d"' % self.product_type.pk, html)
        self.assertIn('data-amount="31.5"', html)
        self.assertIn('data-currency="RUB"', html)


class TestPaymentProcessingPopup(TestCase):
    def test_payment_proessing_popup(self):
        tpl = Template("{% load stripe_processing_popup from stripe %} {% stripe_processing_popup %}")
        html = tpl.render(Context({}))

        self.assertIn('div class="modal payment-processing-popup', html)
