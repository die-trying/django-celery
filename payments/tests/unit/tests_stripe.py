from unittest.mock import patch

from django.test import override_settings
from moneyed import RUB, Money

from elk.utils.testing import TestCase
from payments.stripe import get_stripe_instance, stripe_amount


class TestStripe(TestCase):
    @override_settings(STRIPE_API_KEY='test100500')
    def test_api_key(self):
        stripe = get_stripe_instance()
        self.assertEqual(stripe.api_key, 'test100500')

    @patch.dict('payments.stripe.STRIPE_CURRENCY_MULTIPLIERS', {})
    def test_stripe_amount_default(self):
        cost = Money(20, RUB)

        self.assertEqual(stripe_amount(cost), 2000)  # default multiplier is 100

    @patch.dict('payments.stripe.STRIPE_CURRENCY_MULTIPLIERS', {'RUB': 1000})
    def test_stripe_amount_configured(self):

        cost = Money(20, RUB)

        self.assertEqual(stripe_amount(cost), 20000)
