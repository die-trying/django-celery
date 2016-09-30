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


class TestMarkTrialMiddleware(ClientTestCase):
    def setUp(self):
        self.c.login(username=self.superuser_login, password=self.superuser_password)

    def test_trial_mark_set(self):
        self.c.logout()
        self.c.get('/?trial')
        self.assertTrue(self.c.session['trial'])

    def test_trial_mark_not_set_for_logged_in_user(self):
        self.c.get('/?trial')
        self.assertNotIn('trial', self.c.session.keys())

    def test_trial_mark_not_set_without_get_param(self):
        self.c.logout()
        response = self.c.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('trial', self.c.session.keys())


class TestGuessCountryMiddleware(ClientTestCase):
    def setUp(self):
        self.c.login(username=self.superuser_login, password=self.superuser_password)

    def test_country_guessing_US(self):
        self.c.get('/', REMOTE_ADDR='8.8.8.8')
        self.assertEqual(self.c.session.get('country'), 'US')

    def test_country_guessing_RU(self):
        """
        We need 2 tests to clear session
        """
        self.c.get('/', REMOTE_ADDR='195.218.200.11')
        self.assertEqual(self.c.session.get('country'), 'RU')

    def test_timezone_guessing_passed_when_user_is_registered(self):
        self.c.get('/', REMOTE_ADDR='77.37.209.115')
        self.assertIsNone(self.c.session.get('guessed_timezone'))

    def test_timezone_guessing_RU(self):
        self.c.logout()
        self.c.get('/', REMOTE_ADDR='77.37.209.115')
        self.assertEqual(self.c.session.get('guessed_timezone'), 'Europe/Moscow')

    def test_timezone_guessing_US(self):
        self.c.logout()
        self.c.get('/', REMOTE_ADDR='71.192.161.223')
        self.assertEqual(self.c.session.get('guessed_timezone'), 'America/New_York')
