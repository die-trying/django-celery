from django.test import TestCase


# Create your tests here.

from crm.models import Customer
from products.models import Product1
from hub.models import ActiveSubscription, ActiveLesson


class BuySubscriptionTestCase(TestCase):
    fixtures = ('crm.yaml',)

    def testBuySingleSubscription(self):
        """
        When buing a subscription, all lessons in it should become beeing
        available to the customer
        """
        def _get_lessons_count(product):
            cnt = 0
            for lesson_type in product.LESSONS:
                cnt += len(getattr(product, lesson_type).all())
            return cnt
        product = Product1.objects.get(pk=1)

        s = ActiveSubscription(
            customer=Customer.objects.get(pk=1),
            product=product,
            buy_price=150,
        )
        s.save()

        active_lessons_count = len(ActiveLesson.objects.filter(subscription__product_id=s.pk))
        active_lessons_in_product_count = _get_lessons_count(product)

        self.assertEqual(active_lessons_count, active_lessons_in_product_count, 'When buying a subscription should add all of its available lessons')  # two lessons with natives and four with curators
