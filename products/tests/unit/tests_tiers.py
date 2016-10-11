from mixer.backend.django import mixer

from elk.utils.testing import TestCase
from products.models import Product1, SimpleSubscription, Tier


class TestTier(TestCase):
    fixtures = ('products', 'lessons')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product1 = Product1.objects.get(pk=1)
        cls.product2 = SimpleSubscription.objects.get(pk=1)

    def test_existing_tier(self):
        tier = mixer.blend(Tier, product=self.product1, country='RU', cost=221)
        found = Tier.objects.get_for_product(self.product1, country='RU')

        self.assertEqual(found, tier)

    def test_default_tier(self):
        tier = mixer.blend(Tier, product=self.product1, country='DE', cost=100500, is_default=True)
        found = Tier.objects.get_for_product(self.product1, country='RU')

        self.assertEqual(found, tier)

    def test_single_and_default(self):
        tier = mixer.blend(Tier, product=self.product1, country='RU', cost=221)
        mixer.blend(Tier, product=self.product1, country='DE', cost=100500, is_default=True)

        found = Tier.objects.get_for_product(self.product1, country='RU')

        self.assertEqual(found, tier)  # non-default tier

    def test_tier_without_default(self):
        found = Tier.objects.get_for_product(self.product1, country='RU')
        self.assertIsNone(found)  # should not throw anything

    def test_default_tier_for_other_product(self):
        mixer.blend(Tier, product=self.product2, country='DE', cost=100500, is_default=True)
        found = Tier.objects.get_for_product(self.product1, country='RU')

        self.assertIsNone(found)

    def test_get_tier_by_product(self):
        tier = mixer.blend(Tier, product=self.product1, country='RU', cost=221)

        found = self.product1.get_tier('RU')

        self.assertEqual(found, tier)
