from datetime import datetime
from unittest.mock import MagicMock

from django.core.exceptions import ValidationError
from django.utils import timezone
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market.exceptions import CannotBeScheduled
from market.models import Class
from teachers.models import WorkingHours
from timeline.models import Entry as TimelineEntry


@freeze_time('2005-01-02 03:30')
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
        entry = mixer.blend(TimelineEntry, slots=1, lesson=self.lesson, teacher=self.teacher, start=self.tzdatetime(2016, 12, 1, 1, 10))
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
        entry = mixer.blend(TimelineEntry, slots=1, lesson=self.lesson, teacher=self.teacher, start=self.tzdatetime(2016, 12, 11, 10, 30))
        c.assign_entry(entry)
        c.save()

        fake_cancel_method = MagicMock(return_value=True)
        c.cancel = fake_cancel_method
        c.delete()

        c.refresh_from_db()
        self.assertEqual(fake_cancel_method.call_count, 1)

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
        c.cancel(src='customer')
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
        c.cancel(src='teacher')
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.cancellation_streak, 0)

    def test_cant_cancel_past_classes(self):
        c = self._buy_a_lesson()
        c.schedule(
            teacher=self.teacher,
            date=self.tzdatetime('UTC', 2016, 8, 17, 10, 1),
            allow_besides_working_hours=True,
        )
        c.save()

        with freeze_time('2016-08-17 15:00'):
            with self.assertRaises(ValidationError):
                c.cancel()

    def test_customers_cant_cancel_classes_right_after_they_started(self):
        c = self._buy_a_lesson()
        c.schedule(
            teacher=self.teacher,
            date=self.tzdatetime('UTC', 2016, 8, 17, 10, 1),
            allow_besides_working_hours=True,
        )
        c.save()

        with freeze_time('2016-08-17 10:02'):
            with self.assertRaises(ValidationError):
                c.cancel(src='customer')

    def test_dangrours_cancellation_does_not_throw_exception(self):
        c = self._buy_a_lesson()
        c.schedule(
            teacher=self.teacher,
            date=self.tzdatetime('UTC', 2016, 8, 17, 10, 1),
            allow_besides_working_hours=True,
        )
        c.save()

        with freeze_time('2016-08-17 10:02'):
            c.cancel(src='dangerous-cancellation')
            c.refresh_from_db()
            self.assertFalse(c.is_scheduled)  # class should be cancelled now
