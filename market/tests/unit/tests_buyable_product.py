from elk.utils.testing import TestCase, create_customer
from market.models import Class, Subscription
from products import models as products


class testBuyable(TestCase):
    fixtures = ('crm', 'lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = create_customer()

    def test_subscription_name(self):
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.save()

        self.assertEqual(s.name_for_user, product.name)

    def test_single_class_name(self):
        lesson = products.OrdinaryLesson.get_default()
        c = Class(
            customer=self.customer,
            lesson_type=lesson.get_contenttype()
        )
        c.save()

        self.assertEqual(str(c.name_for_user), str(lesson.type_verbose_name))

    def test_no_deletion(self):
        """
        No buyable product can ever be deleted.
        """
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150
        )
        s.save()
        self.assertEqual(s.active, 1)
        s.delete()
        with self.assertRaises(Subscription.DoesNotExist):
            s.refresh_from_db()
