from datetime import datetime
from unittest.mock import MagicMock

from django.utils import timezone
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market import signals
from market.models import Class
from teachers.models import WorkingHours


class TestClassSignals(TestCase):
    fixtures = ('lessons',)

    def setUp(self):
        self.customer = create_customer()
        self.teacher = create_teacher()
        self.lesson = lessons.OrdinaryLesson.get_default()
        mixer.blend(WorkingHours, teacher=self.teacher, weekday=0, start='13:00', end='15:00')  # monday

    def _buy_a_lesson(self):
        c = Class(
            customer=self.customer,
            lesson=self.lesson
        )
        c.save()
        return c

    def _schedule(self, c, date=datetime(2032, 12, 1, 11, 30)):  # By default it will fail in 16 years, sorry
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        c.schedule(
            teacher=self.teacher,
            date=date,
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
