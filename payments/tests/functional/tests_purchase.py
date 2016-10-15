from moneyed import RUB, Money

from elk.utils.testing import TestCase, create_customer, mock_request
from payments.models import Payment
from payments.tests import mock_stripe
from products.models import Product1


class TestPayments(TestCase):
    fixtures = ('lessons', 'products')

    def setUp(self):
        self.customer = create_customer()
        self.product = Product1.objects.get(pk=1)

    def test_failed_no_shipment(self):
        p = Payment(
            customer=self.customer,
            product=self.product,
            cost=Money(300, RUB)
        )

        mock_stripe(p, success=False)
        p.charge()
        self.assertIsNone(self.customer.subscriptions.first())

    def test_actual_product_shipment(self):
        self.assertIsNone(self.customer.subscriptions.first())

        p = Payment(
            customer=self.customer,
            product=self.product,
            cost=Money(300, RUB)
        )

        mock_stripe(p, success=True)
        p.charge(request=mock_request())

        self.assertIsNotNone(self.customer.subscriptions.first())  # chage() should have shipped the subscription

    def test_history_event_creation(self):
        p = Payment(
            customer=self.customer,
            product=self.product,
            cost=Money(300, RUB)
        )

        mock_stripe(p, success=True)
        p.charge(request=mock_request())

        self.assertIsNotNone(self.customer.payment_events.filter(payment=p).first())
