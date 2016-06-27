from django.test import TestCase


from crm.models import Customer


class CustomerUserModelIntegrationTestCase(TestCase):
    fixtures = ('crm.yaml',)

    def testUsername(self):
        customer_with_user = Customer.objects.get(pk=1)
        self.assertEqual(customer_with_user.full_name, 'Fedor Borshev')
        self.assertEqual(customer_with_user.email, 'f@f213.in')

        customer_without_user = Customer.objects.get(pk=2)
        self.assertEqual(customer_without_user.full_name, 'Vasiliy Poupkine')
        self.assertEqual(customer_without_user.email, 'f@f213.in')
