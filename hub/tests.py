from django.test import TestCase

from elk.utils.reflection import find_ancestors

from crm.models import Customer
from hub.models import ActiveSubscription, Class
import products.models


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

        product = products.models.Product1.objects.get(pk=self.TEST_PRODUCT_ID)

        s = ActiveSubscription(
            customer=Customer.objects.get(pk=self.TEST_CUSTOMER_ID),
            product=product,
            buy_price=150,
        )
        s.save()

        active_lessons_count = Class.objects.filter(subscription_id=s.pk).count()
        active_lessons_in_product_count = _get_lessons_count(product)

        self.assertEqual(active_lessons_count, active_lessons_in_product_count, 'When buying a subscription should add all of its available lessons')  # two lessons with natives and four with curators

    testBuySingleSubscriptionSecondTime = testBuySingleSubscription  # let's test for the second time :-)

    def testDisablingSubscription(self):
        product = products.models.Product1.objects.get(pk=self.TEST_PRODUCT_ID)

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


class BuySingleLessonTestCase(TestCase):
    fixtures = ('crm.yaml',)

    TEST_CUSTOMER_ID = 1

    def testSingleLesson(self):
        """
        Let's but ten lessons at a time
        """
        for lesson_type in find_ancestors(products.models, products.models.Lesson):
            already_bought_lessons = []
            for i in range(0, 10):
                try:
                    s = Class(
                        customer=Customer.objects.get(pk=self.TEST_CUSTOMER_ID),
                        lesson=lesson_type.get_default()  # this should be defined in every lesson
                    )
                    s.save()
                    self.assertTrue(s.pk)
                    self.assertNotIn(s.pk, already_bought_lessons)
                    already_bought_lessons.append(s.pk)
                except NotImplementedError:
                    """
                    Some lessons, ex master classes cannot be bought such way
                    """
                    pass
