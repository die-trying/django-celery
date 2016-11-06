from elk.utils.testing import ClientTestCase, create_teacher


class TestLoginRequiredView(ClientTestCase):
    def setUp(self):
        for i in range(0, 5):
            create_teacher()

    def test_login_ok(self):
        response = self.c.get('/teachers/')  # this view is built from LoginRequiredListView
        self.assertEqual(response.status_code, 200)

    def test_login_required(self):
        self.c.logout()
        response = self.c.get('/teachers/')  # this view is built from LoginRequiredListView

        self.assertRedirectsPartial(response, '/accounts/login')
