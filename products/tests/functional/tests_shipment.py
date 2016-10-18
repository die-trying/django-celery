from elk.utils.testing import TestCase, create_customer
from products.models import Product1, SingleLessonProduct


class TestShipment(TestCase):
    fixtures = ('products', 'lessons')

    def setUp(self):
        self.customer = create_customer()

    def test_subscription_shipment(self):
        product = Product1.objects.get(pk=1)

        product.ship(self.customer)

        shipped = self.customer.subscriptions.first()

        self.assertEqual(shipped.product, product)

    def test_single_lesson_shipment(self):
        product = SingleLessonProduct.objects.first()  # should be created in migration
        self.assertIsNotNone(product.lesson_type)

        product.ship(self.customer)

        shipped = self.customer.classes.first()
        self.assertEqual(shipped.lesson_type, product.lesson_type)
