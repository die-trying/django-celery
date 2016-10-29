from django.core.exceptions import ValidationError

from crm.models import Customer
from elk.utils.testing import TestCase, create_customer
from lessons import models as lessons
from market.models import Class


class CustomerTestCase(TestCase):
    fixtures = ('crm',)

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
            lesson_type=lessons.OrdinaryLesson.get_contenttype(),
            customer=customer
        )
        c.save()
        self.assertTrue(customer.can_schedule_classes())

    def test_invalid_timezone(self):
        """
        Assign an invalid timezone to the customer
        """
        c = create_customer()
        with self.assertRaises(ValidationError):
            c.timezone = 'Noga/Test'
            c.save()
