from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from moneyed import RUB, Money

from elk.utils.testing import ClientTestCase, create_customer
from payments.stripe import stripe_currency
from payments.tests import mock_stripe
from products.models import Product1


class TestPaymentProcessing(ClientTestCase):
    fixtures = ('products', 'lessons')

    def setUp(self):
        self.product = Product1.objects.get(pk=1)
        self.product_type = ContentType.objects.get_for_model(self.product)
        self.customer = create_customer(password='AhYei6asho1w')

        self.cost = Money(300, RUB)

        self.c.logout()
        self.c.login(username=self.customer.user.username, password="AhYei6asho1w")

    @patch('payments.models.get_stripe_instance')
    def test_normal_processing(self, stripe_instance):
        stripe_instance.return_value = mock_stripe(success=True)
        response = self.c.post('/payments/process/', {
            'product_id': self.product.pk,
            'product_type': self.product_type.pk,
            'amount': self.cost.amount,
            'currency': stripe_currency(self.cost),
            'stripeToken': 'tsttkn',
        })

        self.assertRedirects(response, '/payments/%d/%d/success/' % (self.product_type.pk, self.product.pk))

        self.assertIsNotNone(self.customer.subscriptions.first())  # customer should have subscription now

    @patch('payments.models.get_stripe_instance')
    def test_success_page(self, stripe_instance):
        stripe_instance.return_value = mock_stripe(success=True)
        response = self.c.post('/payments/process/', {
            'product_id': self.product.pk,
            'product_type': self.product_type.pk,
            'amount': self.cost.amount,
            'currency': stripe_currency(self.cost),
            'stripeToken': 'tsttkn',
        }, follow=True)

        self.assertTemplateUsed(response, 'payments/result_base.html')
        self.assertEqual(response.context['product'], self.product)

    @patch('payments.models.get_stripe_instance')
    def test_stripe_failure(self, stripe_instance):
        stripe_instance.return_value = mock_stripe(success=False)

        response = self.c.post('/payments/process/', {
            'product_id': self.product.pk,
            'product_type': self.product_type.pk,
            'amount': self.cost.amount,
            'currency': stripe_currency(self.cost),
            'stripeToken': 'tsttkn',
        })

        self.assertRedirects(response, '/payments/%d/%d/failure/' % (self.product_type.pk, self.product.pk))

        self.assertIsNone(self.customer.subscriptions.first())  # customer should not gain with subscription

    @patch('payments.models.get_stripe_instance')
    def test_error_page(self, stripe_instance):
        stripe_instance.return_value = mock_stripe(success=False)
        response = self.c.post('/payments/process/', {
            'product_id': self.product.pk,
            'product_type': self.product_type.pk,
            'amount': self.cost.amount,
            'currency': stripe_currency(self.cost),
            'stripeToken': 'tsttkn',
        }, follow=True)

        self.assertTemplateUsed(response, 'payments/result_failure.html')
        self.assertIn('testing', response.context['msg'])  # mocked error message should appear in the template

    def test_bad_product_type(self):
        result = self.c.post('/payments/process/', {
            'product_id': self.product.pk,
            'product_type': ContentType.objects.get_for_model(self.product).pk + 100500,  # BAD
            'amount': self.cost.amount,
            'currency': stripe_currency(self.cost),
            'stripeToken': 'tsttkn',
        })
        self.assertEqual(result.status_code, 404)

    def test_bad_product(self):
        result = self.c.post('/payments/process/', {
            'product_id': '100500',  # BAD
            'product_type': ContentType.objects.get_for_model(self.product).pk,
            'amount': self.cost.amount,
            'currency': stripe_currency(self.cost),
            'stripeToken': 'tsttkn',
        })
        self.assertEqual(result.status_code, 404)
