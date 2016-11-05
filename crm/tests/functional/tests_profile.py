from elk.utils.testing import ClientTestCase, create_customer


class TestCustomerProfile(ClientTestCase):
    def setUp(self):
        self.customer = create_customer(password='Taich8aeng8M')
        self.c.logout()
        self.c.login(username=self.customer.user.username, password='Taich8aeng8M')

    def test_no_anon(self):
        self.c.logout()
        response = self.c.get('/accounts/profile/')
        self.assertRedirectsPartial(response, 'accounts/login')

    def test_get(self):
        self.customer.skype = 'tst_skype_acc'
        self.customer.save()

        response = self.c.get('/accounts/profile/')

        with self.assertHTML(response, '#id_skype') as (skype,):
            self.assertEqual(skype.value, 'tst_skype_acc')

        with self.assertHTML(response, '#customer-profile__email>a') as (email,):
            self.assertEqual(email.text, self.customer.user.email)

    def test_post(self):
        response = self.c.post('/accounts/profile/', {
            'skype': 'tst_skype_updated',
            'timezone': 'US/Alaska',
        })
        self.assertRedirectsPartial(response, '/accounts/profile/')

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.skype, 'tst_skype_updated')
        self.assertEqual(str(self.customer.timezone), 'US/Alaska')
