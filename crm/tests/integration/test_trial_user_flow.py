from elk.utils.testing import ClassIntegrationTestCase


class TestFullTrialUserFlow(ClassIntegrationTestCase):
    def setUp(self):
        super().setUp()

        self.customer.user.set_password('vuF3theiyivo')
        self.customer.user.save()

        self.c.logout()
        self.c.login(username=self.customer.user.username, password='vuF3theiyivo')

    def test_full_trial_user_flow(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('acc/_greetings/alpha_greeting.html')

        self.customer.add_trial_lesson()

        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('acc/_greetings/trial_greeting.html')

        self.lesson = self.customer.classes.first().lesson_type.model_class().get_default()  # set to schedule a trial lesson in the parent class

        self._schedule(self.customer.classes.first(), self._create_entry())

        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('acc/_greetings/trial-scheduled_greeting.html')
