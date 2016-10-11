from mixer.backend.django import mixer

from elk.utils.testing import TestCase
from lessons import models as lessons
from products.models import Product1, SimpleSubscription, Tier


class TestSubscriptionDisplayTestCase(TestCase):
    fixtures = ('crm', 'lessons', 'products')

    def setUp(self):
        self.product = Product1.objects.get(pk=1)

    def test_lesson_types(self):
        lesson_types = list(self.product.lesson_types())
        self.assertEqual(len(lesson_types), 5)
        self.assertEqual(lesson_types[0], lessons.OrdinaryLesson.get_contenttype())
        self.assertEqual(lesson_types[4], lessons.MasterClass.get_contenttype())

    def test_lessons(self):
        bundled_lessons = list(self.product.lessons())
        self.assertEqual(len(bundled_lessons), 5)
        self.assertEqual(bundled_lessons[0].first().get_contenttype(), lessons.OrdinaryLesson.get_contenttype())
        self.assertEqual(bundled_lessons[4].first().get_contenttype(), lessons.MasterClass.get_contenttype())

    def test_classes_by_lesson_type(self):
        ordinary_lesson_type = lessons.OrdinaryLesson.get_contenttype()
        master_class_type = lessons.MasterClass.get_contenttype()

        ordinary_lessons = self.product.classes_by_lesson_type(ordinary_lesson_type)
        master_classes = self.product.classes_by_lesson_type(master_class_type)

        self.assertEqual(len(ordinary_lessons), 5)  # fill free to modify this if you've changed the first subcription
        self.assertEqual(len(master_classes), 1)


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
