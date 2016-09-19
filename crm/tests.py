from mixer.backend.django import mixer

from crm.models import Customer
from elk.utils.testing import TestCase, create_customer
from lessons import models as lessons
from market.models import Class


class CustomerTestCase(TestCase):
    fixtures = ('crm.yaml',)

    def test_username(self):
        """
        Customer objects with assigned django user should take user data from
        the django table.
        """
        customer_with_user = Customer.objects.get(pk=1)
        self.assertEqual(customer_with_user.full_name, 'Fedor Borshev')
        self.assertEqual(customer_with_user.first_name, 'Fedor')
        self.assertEqual(customer_with_user.last_name, 'Borshev')
        self.assertEqual(customer_with_user.email, 'f@f213.in')

        customer_without_user = Customer.objects.get(pk=2)
        self.assertEqual(customer_without_user.full_name, 'Vasiliy Poupkine')
        self.assertEqual(customer_without_user.first_name, 'Vasiliy')
        self.assertEqual(customer_without_user.last_name, 'Poupkine')
        self.assertEqual(customer_without_user.email, 'f@f213.in')

    def test_can_cancel_classes(self):
        customer = create_customer()

        self.assertTrue(customer.can_cancel_classes())
        customer.cancellation_streak = 5
        customer.max_cancellation_count = 5
        self.assertFalse(customer.can_cancel_classes())

    def test_can_schedule_classes(self):
        customer = create_customer()

        self.assertFalse(customer.can_schedule_classes())
        c = Class(
            lesson=mixer.blend(lessons.OrdinaryLesson, customer=customer),
            customer=customer
        )
        c.save()
        self.assertTrue(customer.can_schedule_classes())
