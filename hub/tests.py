from django.test import TestCase


# Create your tests here.

from crm.models import Customer
from products.models import Product1
from hub.models import ActiveSubscription, Class


class BuySubscriptionTestCase(TestCase):
    fixtures = ('crm.yaml',)
    TEST_PRODUCT_ID = 1
    TEST_CUSTOMER_ID = 1

    def testBuySingleSubscription(self):
        """
        When buing a subscription, all lessons in it should become beeing
        available to the customer
        """

        def _get_lessons_count(product):
            cnt = 0
            for lesson_type in product.LESSONS:
                cnt += getattr(product, lesson_type).all().count()
            return cnt

        product = Product1.objects.get(pk=self.TEST_PRODUCT_ID)

        s = ActiveSubscription(
            customer=Customer.objects.get(pk=self.TEST_CUSTOMER_ID),
            product=product,
            buy_price=150,
        )
        s.save()

        active_lessons_count = Class.objects.filter(subscription_id=s.pk).count()
        active_lessons_in_product_count = _get_lessons_count(product)

        self.assertEqual(active_lessons_count, active_lessons_in_product_count, 'When buying a subscription should add all of its available lessons')  # two lessons with natives and four with curators

    testBuySingleSubscriptionSecondTime = testBuySingleSubscription

    def testDisablingSubscription(self):
        product = Product1.objects.get(pk=self.TEST_PRODUCT_ID)

        s = ActiveSubscription(
            customer=Customer.objects.get(pk=self.TEST_CUSTOMER_ID),
            product=product,
            buy_price=150,
        )
        s.save()

        for lesson in s.classes.all():
            self.assertEqual(lesson.active, 1)

        # now, disable the subscription for any reason
        s.active = 0
        s.save()
        for lesson in s.classes.all():
            self.assertEqual(lesson.active, 0, 'Every lesson in subscription should become inactive now')
