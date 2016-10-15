from django.test import override_settings

from elk.utils.testing import TestCase
from payments.stripe import get_stripe


class TestStripe(TestCase):
    @override_settings(STRIPE_API_KEY='test100500')
    def test_api_key(self):
        stripe = get_stripe()
        self.assertEqual(stripe.api_key, 'test100500')
