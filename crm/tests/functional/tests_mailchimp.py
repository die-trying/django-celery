import csv

from elk.utils.testing import ClientTestCase, create_customer


class TestMailchimpExport(ClientTestCase):
    def setUp(self):
        self.customers = []
        for i in range(0, 10):
            self.customers.append(create_customer())

    def test_csv_export(self):
        ids = ','.join([str(customer.pk) for customer in self.customers])

        response = self.c.get('/crm/mailchimp_csv/%s' % ids)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8').strip().split('\n')
        got = list(csv.reader(content))

        self.assertEqual(len(got), 11)  # header + 10 customers

        for i in range(0, 10):
            self.assertListEqual(got[i + 1], [
                self.customers[i].email,
                self.customers[i].first_name,
                self.customers[i].last_name,
            ])

    def test_staff_only(self):
        someone = create_customer(password='bulitaeM1cha')
        self.c.logout()
        self.c.login(username=someone.user.username, password='bulitaeM1cha')

        response = self.c.get('/crm/mailchimp_csv/%d' % self.customers[0].pk)
        self.assertRedirectsPartial(response, '/accounts/login')
