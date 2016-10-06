from unittest.mock import patch

from django.core import mail
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import ClassIntegrationTestCase, create_customer
from timeline.tasks import notify_15min_to_class


class TestStartingSoonEmail(ClassIntegrationTestCase):
    @patch('market.signals.Owl')
    def test_single_class_pre_start_notification(self, Owl):
        entry = self._create_entry()
        c = self._buy_a_lesson()
        self._schedule(c, entry)

        with freeze_time('2032-09-13 15:46'):   # entry will start in 14 minutes
            for i in range(0, 10):  # run this 10 times to check for repietive emails — all notifications should be sent one time
                notify_15min_to_class()

        self.assertEqual(len(mail.outbox), 2)  # if this test fails, carefully check the timezone you are in

        out_emails = [outbox.to[0] for outbox in mail.outbox]

        self.assertIn(self.host.user.email, out_emails)
        self.assertIn(self.customer.user.email, out_emails)

    @patch('market.signals.Owl')
    def test_two_classes_pre_start_notification(self, Owl):
        self.lesson = mixer.blend('lessons.MasterClass', host=self.host, slots=5)

        other_customer = create_customer()
        first_customer = self.customer

        entry = self._create_entry()
        entry.slots = 5
        entry.save()

        c = self._buy_a_lesson()
        self._schedule(c, entry)

        self.customer = other_customer
        c1 = self._buy_a_lesson()
        self._schedule(c1, entry)
        with freeze_time('2032-09-13 15:46'):   # entry will start in 14 minutes
            for i in range(0, 10):  # run this 10 times to check for repietive emails — all notifications should be sent one time
                notify_15min_to_class()

        self.assertEqual(len(mail.outbox), 3)  # if this test fails, carefully check the timezone you are in

        out_emails = [outbox.to[0] for outbox in mail.outbox]

        self.assertIn(self.host.user.email, out_emails)
        self.assertIn(first_customer.user.email, out_emails)
        self.assertIn(other_customer.user.email, out_emails)
