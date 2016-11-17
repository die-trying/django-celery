from elk.utils.testing import TestCase, create_customer
from market.models import Class, Subscription
from products import models as products


class BuySubscriptionTestCase(TestCase):
    fixtures = ('crm', 'lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = create_customer()

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

        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.save()

        active_lessons_count = Class.objects.filter(subscription_id=s.pk).count()
        active_lessons_in_product_count = _get_lessons_count(product)

        # two lessons with natives and four with curators
        self.assertEqual(active_lessons_count, active_lessons_in_product_count, 'When buying a subscription should add all of its available lessons')

    test_second_time = test_buy_a_single_subscription  # let's test for the second time :-)

    def test_store_class_source(self):
        """
        When buying a subcription, every purchased class should have a sign
        about that it's purchased buy subscription.
        """

        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150
        )
        s.save()

        for c in s.classes.all():
            self.assertEqual(c.buy_source, 'subscription')

    def test_disabling_subscription(self):
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.save()

        for c in s.classes.all():
            self.assertFalse(c.is_fully_used)

        # now, disable the subscription for any reason
        s.deactivate()
        s.save()
        for c in s.classes.all():
            self.assertTrue(c.is_fully_used, 'Every class in subscription should become inactive now')

    def test_mark_as_fully_used(self):
        """
        Buy a subscription, than mark all classes from it as used, one by one
        """
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.save()

        self.assertFalse(s.is_fully_used)

        lessons = []
        for lesson in s.classes.all():
            lessons.append(lesson)

        for lesson in lessons[:-1]:
            lesson.mark_as_fully_used()
            self.assertFalse(s.is_fully_used)

        lessons[-1].mark_as_fully_used()
        self.assertTrue(s.is_fully_used)  # the last lesson should have marked it's parent subscription as fully used
