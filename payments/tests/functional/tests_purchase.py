from moneyed import RUB, Money

from elk.utils.testing import TestCase, create_customer, mock_request
from payments.models import StripePayment
from payments.tests import patch_stripe
from products.models import Product1


class TestPayments(TestCase):
    fixtures = ('lessons', 'products')

    def setUp(self):
        self.customer = create_customer()
        self.product = Product1.objects.get(pk=1)

    def test_failed_no_shipment(self):
        p = StripePayment(
            customer=self.customer,
            product=self.product,
            cost=Money(300, RUB)
        )

        patch_stripe(p, success=False)
        p.charge()
        self.assertIsNone(self.customer.subscriptions.first())

    def test_actual_product_shipment(self):
        self.assertIsNone(self.customer.subscriptions.first())

        p = StripePayment(
            customer=self.customer,
            product=self.product,
            cost=Money(300, RUB)
        )

        patch_stripe(p, success=True)
        p.charge(request=mock_request())

        self.assertIsNotNone(self.customer.subscriptions.first())  # chage() should have shipped the subscription

    def test_charge_result(self):
        """
        Charge() should return a boolean result of stripe communication
        """
        p = StripePayment(
            customer=self.customer,
            product=self.product,
            cost=Money(300, RUB)
        )

        patch_stripe(p, success=True)
        self.assertTrue(p.charge(request=mock_request()))

        patch_stripe(p, success=False)
        self.assertFalse(p.charge())
