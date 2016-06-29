from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model

from crm.models import Customer


class CustomerUserModelIntegrationTestCase(TestCase):
    fixtures = ('crm.yaml',)

    def testUsername(self):
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

    def testCustomerCreationThroughUser(self):
        """
        Every newly created user object should have an assigned customer object
        """
        User = get_user_model()
        user = mixer.blend(User, email='test@test.email')

        user.save()

        self.assertTrue(user.pk)
        self.assertEqual(user.customer.email, 'test@test.email')
