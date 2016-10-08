import json

from elk.utils.testing import ClientTestCase, create_customer


class TestIssueCreation(ClientTestCase):
    def setUp(self):
        self.customer = create_customer()
        self.customer.user.set_password('Vae7peeVafi8')
        self.customer.user.save()

        self.c.logout()
        self.c.login(username=self.customer.user.username, password='Vae7peeVafi8')

    def test_issue_creation(self):
        response = self.c.post('/crm/issue/', {
            'body': 'Help! Eearthquake!',
        })
        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content.decode('utf-8'))
        self.assertIsNotNone(result['pk'])

        saved_issue = self.customer.issues.get(body='Help! Eearthquake!')
        self.assertIsNotNone(saved_issue)
        self.assertEqual(saved_issue.pk, result['pk'])

    def test_issue_without_body(self):
        response = self.c.post('/crm/issue/', {
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(self.customer.issues.all()), 0)

    def test_no_creation_withou_login(self):
        self.c.logout()
        response = self.c.post('/crm/issue/', {
            'body': 'Help! Eearthquake!',
        })
        self.assertEqual(response.status_code, 302)
