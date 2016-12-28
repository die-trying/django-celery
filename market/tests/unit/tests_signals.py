from unittest.mock import MagicMock

from django.contrib.admin.models import LogEntry

from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market import signals
from market.models import Class, Subscription
from products.models import Product1


class TestSubscriptionSignals(TestCase):
    fixtures = ('lessons', 'products')

    def setUp(self):
        self.customer = create_customer()
        self.subscription = Subscription(
            customer=self.customer,
            product=Product1.objects.get(pk=1),
            buy_price=150,
        )
        self.deactivator = create_customer().user

    def test_deactivation_signal_is_beeing_sent(self):
        handler = MagicMock()
        signals.subscription_deactivated.connect(handler)
        self.subscription.deactivate()
        self.assertEqual(handler.call_count, 1)

    def test_log_entry_creation(self):
        self.subscription.deactivate(user=self.deactivator)

        log_entry = LogEntry.objects.first()
        self.assertEqual(log_entry.user, self.deactivator)
        self.assertIn('deactivated', log_entry.change_message)


class TestClassSignals(TestCase):
    fixtures = ['lessons']

    def setUp(self):
        self.customer = create_customer()
        self.teacher = create_teacher(works_24x7=True)
        self.lesson = lessons.OrdinaryLesson.get_contenttype()

    def _buy_a_lesson(self):
        c = Class(
            customer=self.customer,
            lesson_type=self.lesson
        )
        c.save()
        return c

    def _schedule(self, c):
        c.schedule(
            teacher=self.teacher,
            date=self.tzdatetime(2032, 12, 1, 11, 30),
            allow_besides_working_hours=True,
        )
        c.save()
        c.refresh_from_db()
        self.assertTrue(c.is_scheduled)
        return c

    def test_scheduled_signal_is_beeing_sent(self):
        handler = MagicMock()
        c = self._buy_a_lesson()
        signals.class_scheduled.connect(handler)
        self._schedule(c)
        self.assertEqual(handler.call_count, 1)

    def test_scheduled_class_signal_called_once(self):
        handler = MagicMock()
        c = self._buy_a_lesson()
        signals.class_scheduled.connect(handler)
        self._schedule(c)
        self.assertEqual(handler.call_count, 1)

        for i in range(0, 5):
            c.save()

        self.assertEqual(handler.call_count, 1)  # signal should be saved only once

    def test_cancellation_signal_is_beeing_sent(self):
        c = self._buy_a_lesson()
        self._schedule(c)
        handler = MagicMock()
        signals.class_cancelled.connect(handler)
        c.cancel()
        self.assertEqual(handler.call_count, 1)
