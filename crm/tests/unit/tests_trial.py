from django.core import mail
from django.test import override_settings
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer


class TestTrial(TestCase):
    fixtures = ('lessons',)

    def setUp(self):
        self.customer = create_customer()

    def test_add_trial_lesson(self):
        self.customer.add_trial_lesson()
        self.customer.refresh_from_db()

        self.assertEqual(self.customer.classes.count(), 1)

    @override_settings(EMAIL_ASYNC=False)
    def test_trial_letter(self):
        self.customer.add_trial_lesson()
        self.assertEqual(len(mail.outbox), 1)  # should send the greeting email to customer
        self.assertIn(self.customer.user.email, mail.outbox[0].to)

    def test_is_trial_user_on_the_new_customer(self):
        self.assertFalse(self.customer.is_trial_user())

    def test_is_trial_user(self):
        self.customer.add_trial_lesson()
        self.customer.refresh_from_db()

        self.assertTrue(self.customer.is_trial_user())

    def test_is_trial_user_with_classes(self):
        """
        When user has some other classes except the trial one, don't mark him as
        a trial user.
        """
        self.customer.add_trial_lesson()
        self.customer.classes.add(mixer.blend('market.Class', customer=self.customer))

        self.assertFalse(self.customer.is_trial_user())

    def test_is_trial_user_when_trial_has_finished(self):
        """
        Mark the only trial class as used
        """
        self.customer.add_trial_lesson()
        trial_class = self.customer.classes.first()
        trial_class.mark_as_fully_used()
        self.assertFalse(self.customer.is_trial_user())

    def test_trial_lesson_is_scheduled(self):
        self.customer.add_trial_lesson()
        self.assertFalse(self.customer.trial_lesson_is_scheduled())

        trial_class = self.customer.classes.first()
        trial_class.is_scheduled = True
        trial_class.save()

        self.assertFalse(self.customer.trial_lesson_is_scheduled())

    def test_trial_lesson_is_scheduled_on_non_trial_user(self):
        """
        Test misuse of the method, i.e. on a fresh-created customer
        """
        self.assertFalse(self.customer.trial_lesson_is_scheduled())
