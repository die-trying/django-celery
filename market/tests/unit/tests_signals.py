from unittest.mock import MagicMock

from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market import signals
from market.models import Class


class TestClassSignals(TestCase):
    fixtures = ('lessons',)

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

    def test_scheduled_signal(self):
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

    def test_cancellation_signal(self):
        c = self._buy_a_lesson()
        self._schedule(c)
        handler = MagicMock()
        signals.class_cancelled.connect(handler)
        c.cancel()
        self.assertEqual(handler.call_count, 1)
