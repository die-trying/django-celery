from elk.utils.testing import ClientTestCase, create_customer


class TestTimezoneMiddleware(ClientTestCase):
    def setUp(self):
        self.customer = create_customer(timezone='Africa/Addis_Ababa')
        self.customer.user.username = 'timezone_tester'
        self.customer.user.set_password('123')
        self.customer.user.save()

        self.c.logout()
        self.c.login(username='timezone_tester', password='123')

    def test_timezone_template_context(self):
        self.assertIsNotNone(self.customer.timezone)

        response = self.c.get('/')

        self.assertEqual(response.context['user'], self.customer.user)  # we should now be logged in with generated user, not the default one
        self.assertEqual(response.context['TIME_ZONE'], 'Africa/Addis_Ababa')


class TestGuessCountryMiddleware(ClientTestCase):
    def test_country_guessing(self):
        self.c.get('/', REMOTE_ADDR='8.8.8.8')
        self.assertEqual(self.c.session.get('country'), 'US')

        self.c.get('/', REMOTE_ADDR='195.218.200.11')
        self.assertEqual(self.c.session.get('country'), 'RU')
