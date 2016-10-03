from datetime import datetime
from unittest.mock import MagicMock

from django.utils import timezone
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market.exceptions import CannotBeScheduled
from market.models import Class
from teachers.models import WorkingHours
from timeline.models import Entry as TimelineEntry


class TestScheduleLowLevel(TestCase):
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

    def test_assign_entry(self):
        """ Not poluting timeline with existing timeline entries """
        c = self._buy_a_lesson()
        entry = mixer.blend(TimelineEntry, slots=1, lesson=self.lesson, teacher=self.teacher)
        entry.save = MagicMock(return_value=None)

        c.assign_entry(entry)

        entry.save.assert_not_called()

    def test_schedule_auto_entry(self):
        """ Not poluting timeline when generating timeline entry """
        c = self._buy_a_lesson()
        c.schedule(
            teacher=self.teacher,
            date=self.tzdatetime(2016, 12, 1, 7, 25),  # monday
            allow_besides_working_hours=True,
        )
        self.assertIsNone(c.timeline.pk)
        c.timeline.save = MagicMock(return_value=None)
        c.timeline.save.assert_not_called()

    def test_schedule_auto_entry_only_within_working_hours(self):
        c = self._buy_a_lesson()
        with self.assertRaises(CannotBeScheduled):
            c.schedule(
                teacher=self.teacher,
                date=self.tzdatetime(2016, 12, 1, 7, 27)  # wednesday
            )
            c.save()

    def test_deletion_of_a_scheduled_class(self):
        """
        Deletion of a scheduled class should just call it's
        unscheduling mechanism.
        """
        c = self._buy_a_lesson()
        entry = mixer.blend(TimelineEntry, slots=1, lesson=self.lesson, teacher=self.teacher)
        c.assign_entry(entry)
        c.save()

        unschedule = MagicMock(return_value=True)
        c.unschedule = unschedule
        c.delete()

        c.refresh_from_db()
        unschedule.assert_any_call()

    def test_deletion_of_an_unscheduled_class(self):
        """
        Deletion of an unscheduled class should be like any other
        :model:`market.Buyable`.
        """
        c = self._buy_a_lesson()
        unschedule = MagicMock(return_value=True)
        c.unschedule = unschedule

        c.delete()
        with self.assertRaises(Class.DoesNotExist):
            c.refresh_from_db()

        unschedule.assert_not_called()

    def test_increase_cancellation_count(self):
        """
        Every cancellation caused by customer should increase its cancellation count
        """
        c = self._buy_a_lesson()
        c.schedule(
            teacher=self.teacher,
            date=timezone.make_aware(datetime(2016, 12, 1, 7, 25)),  # monday
            allow_besides_working_hours=True,
        )
        c.save()
        self.assertEqual(self.customer.cancellation_streak, 0)
        c.unschedule(src='customer')
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.cancellation_streak, 1)

    def test_dont_increase_canellation_count(self):
        """
        Cancel caused by teacher should not increase user's cancellation count
        """
        c = self._buy_a_lesson()
        c.schedule(
            teacher=self.teacher,
            date=timezone.make_aware(datetime(2016, 12, 1, 7, 25)),  # monday
            allow_besides_working_hours=True,
        )
        c.save()
        self.assertEqual(self.customer.cancellation_streak, 0)
        c.unschedule(src='teacher')
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.cancellation_streak, 0)
