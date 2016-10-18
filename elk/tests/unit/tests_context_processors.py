from unittest.mock import patch

from django.test import override_settings

from elk.utils.testing import ClientTestCase, create_customer


class TestGreetingContextProcessor(ClientTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = create_customer()
        cls.customer.user.set_password('Gaew1queeTie')
        cls.customer.user.save()

    def setUp(self):
        self.c.logout()
        self.c.login(username=self.customer.user.username, password='Gaew1queeTie')

    @patch('crm.models.Customer.get_greeting_type')
    def test_greeting_context(self, get_greeting_type):
        get_greeting_type.return_value = 'subscription-active'

        response = self.c.get('/')

        self.assertEqual(response.context['GREETING'], 'subscription-active')

    def test_greeting_context_via_get(self):
        """
        Test for an abiltiy to pass greeting type as GET argument for adjusting templates
        """

        response = self.c.get('/?greeting=subscription-finished')
        self.assertEqual(response.context['GREETING'], 'subscription-finished')

    def test_greeting_get_bad_input(self):
        """
        Check for malicious input in get greeting
        """
        response = self.c.get('/?greeting=/etc/passwd')
        self.assertEqual(response.context['GREETING'], 'empty')

    def test_greeting_without_user(self):
        """
        There should be no greeting in template context when user is logged out
        """
        self.c.logout()
        response = self.c.get('/', follow=True)

        self.assertNotIn('GREETING', response.context)


class TestSimpleContextProcessors(ClientTestCase):
    @override_settings(SUPPORT_EMAIL='t@tt.tst')
    def test_support_email(self):
        response = self.c.get('/')
        self.assertEqual(response.context['SUPPORT_EMAIL'], 't@tt.tst')

    @override_settings(STRIPE_PK='tst100500')
    def test_stripe_pk(self):
        response = self.c.get('/')
        self.assertEqual(response.context['STRIPE_PK'], 'tst100500')
