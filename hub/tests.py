from django.test import TestCase


# Create your tests here.

from crm.models import Customer
from products.models import Product1
from hub.models import ActiveSubscription, ActiveLesson


class BuySubscriptionTestCase(TestCase):
    fixtures = ('crm.yaml',)

    def testCreatingLessons(self):
        s = ActiveSubscription(
            customer=Customer.objects.get(pk=1),
            product=Product1.objects.get(pk=1),
            buy_price=150,
        )
        s.save()

        active_lessons = ActiveLesson.objects.filter(subscription__product_id=s.pk)

        self.assertEqual(len(active_lessons), 6, 'When buying a subscription should add all of its available lessons')  # two lessons with natives and four with curators
