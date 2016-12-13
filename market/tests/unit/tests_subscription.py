from datetime import timedelta

from freezegun import freeze_time

from elk.utils.testing import TestCase, create_customer
from market.models import Subscription
from products.models import Product1


class TestSUbscriptionUnit(TestCase):
    fixtures = ('products', 'lessons')

    @classmethod
    def setUpTestData(cls):
        cls.product = Product1.objects.get(pk=1)
        cls.product.duration = timedelta(days=5)
        cls.product.save()

        cls.customer = create_customer()

    @freeze_time('2032-12-01 12:00')
    def test_is_due(self):
        s = Subscription(
            customer=self.customer,
            product=self.product,
            buy_price=150
        )
        s.save()

        self.assertFalse(s.is_due())
        with freeze_time('2032-12-07 12:00'):  # move 6 days forward
            self.assertTrue(s.is_due())
