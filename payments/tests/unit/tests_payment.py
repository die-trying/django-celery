from mixer.backend.django import mixer
from moneyed import RUB, Money

from elk.utils.testing import TestCase, create_customer
from payments.models import Payment
from products.models import Product1


class TestPaymentUnit(TestCase):
    fixtures = ('products', 'lessons')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = Product1.objects.get(pk=1)

    def setUp(self):
        self.customer = create_customer()

    def test_stripe_amount_default(self):
        p = mixer.blend(
            Payment,
            customer=self.customer,
            product=self.product,
        )

        p.cost = Money(20, RUB)
        p.save()

        p.STRIPE_CURRENCY_MULTIPLIERS = {}  # disable all stock multipliers

        self.assertEqual(p._stripe_amount(), 2000)  # default multiplier is 100

    def test_stripe_amount_configured(self):
        p = mixer.blend(
            Payment,
            customer=self.customer,
            product=self.product,
        )

        p.cost = Money(20, RUB)
        p.save()

        p.STRIPE_CURRENCY_MULTIPLIERS = {
            'RUB': 1000,
        }

        self.assertEqual(p._stripe_amount(), 20000)
