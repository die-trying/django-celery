from datetime import timedelta
from unittest.mock import MagicMock

from elk.utils.testing import TestCase, create_customer
from market.models import Class, Subscription
from products import models as products


class BuySubscriptionTestCase(TestCase):
    fixtures = ('lessons', 'products')
    TEST_PRODUCT_ID = 1

    @classmethod
    def setUpTestData(cls):
        cls.customer = create_customer()
        cls.product = products.Product1.objects.get(pk=cls.TEST_PRODUCT_ID)

    def setUp(self):
        self.subscription = Subscription(
            customer=self.customer,
            product=self.product,
            buy_price=150
        )
        self.subscription.save()

    def test_buy_a_single_subscription(self):
        """
        When buing a subscription, all lessons in it should become beeing
        available to the customer
        """

        # TODO: Clean this up
        def _get_lessons_count(product):
            cnt = 0
            for lesson_type in product.LESSONS:
                cnt += getattr(product, lesson_type).all().count()
            return cnt

        active_lessons_count = Class.objects.filter(subscription=self.subscription).count()
        active_lessons_in_product_count = _get_lessons_count(self.product)

        # two lessons with natives and four with curators
        self.assertEqual(active_lessons_count, active_lessons_in_product_count, 'When buying a subscription should add all of its available lessons')

    test_second_time = test_buy_a_single_subscription  # let's test for the second time :-)

    def test_store_class_source(self):
        """
        When buying a subscription, every purchased class should have a sign
        about that it's purchased buy subscription.
        """
        for c in self.subscription.classes.all():
            self.assertEqual(c.buy_source, 'subscription')

    def test_subbscription_stores_duration(self):
        """
        Every new subscription should take its duration from the purchaed product
        """
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        product.duration = timedelta(days=221)
        product.save()

        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150
        )
        s.save()

        self.assertEqual(s.duration, timedelta(days=221))

    def test_disabling_subscription(self):
        for c in self.subscription.classes.all():
            self.assertFalse(c.is_fully_used)

        # now, disable the subscription for any reason
        self.subscription.deactivate()
        self.subscription.save()
        for c in self.subscription.classes.all():
            self.assertTrue(c.is_fully_used, 'Every class in subscription should become inactive now')

    def test_mark_as_fully_used(self):
        """
        Buy a subscription, than mark all classes from it as used, one by one
        """
        self.assertFalse(self.subscription.is_fully_used)

        classes = [c for c in self.subscription.classes.all()]

        for c in classes[:-1]:
            c.mark_as_fully_used()
            self.assertFalse(self.subscription.is_fully_used)

        classes[-1].mark_as_fully_used()
        self.assertTrue(self.subscription.is_fully_used)  # the last lesson should have marked it's parent subscription as fully used

    def test_finished_class_sets_the_first_lesson_date_of_the_parent_subscription(self, *args):
        first_class = self.subscription.classes.first()
        first_class.save()

        self.subscription.update_first_lesson_date = MagicMock(spec=True)
        first_class.mark_as_fully_used()
        self.assertEqual(self.subscription.update_first_lesson_date.call_count, 1)
