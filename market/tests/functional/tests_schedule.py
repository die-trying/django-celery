from unittest.mock import MagicMock, patch

from django.core import mail
from django.test import override_settings
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market.exceptions import CannotBeScheduled
from market.models import Class
from products import models as products
from timeline.models import Entry as TimelineEntry


@freeze_time('2005-12-01 01:30')
class ScheduleTestCase(TestCase):
    fixtures = ('crm', 'lessons')

    def setUp(self):
        self.host = create_teacher()
        self.customer = create_customer()

    def _buy_a_lesson(self, lesson):
        c = Class(
            customer=self.customer,
            lesson=lesson
        )
        c.save()
        return c

    def test_schedule_simple(self):
        """
        Generic test to schedule and unschedule a class
        """
        lesson = products.OrdinaryLesson.get_default()

        entry = mixer.blend(TimelineEntry, teacher=self.host, slots=1, lesson=lesson, start=self.tzdatetime(2032, 12, 12))
        purchased_class = self._buy_a_lesson(lesson)

        self.assertFalse(purchased_class.is_scheduled)
        self.assertTrue(entry.is_free)

        purchased_class.assign_entry(entry)  # schedule a class
        purchased_class.save()

        self.assertTrue(purchased_class.is_scheduled)
        self.assertFalse(entry.is_free)
        self.assertEquals(entry.classes.first().customer, self.customer)

        purchased_class.cancel()
        purchased_class.save()
        self.assertFalse(purchased_class.is_scheduled)
        self.assertTrue(entry.is_free)

    def test_schedule_auto_entry(self):
        """
        Chedule a class without a timeline entry
        """
        lesson = products.OrdinaryLesson.get_default()
        c = self._buy_a_lesson(lesson)
        c.schedule(
            teacher=self.host,
            date=self.tzdatetime(2016, 8, 17, 10, 1),
            allow_besides_working_hours=True,
        )
        c.save()

        self.assertIsInstance(c.timeline, TimelineEntry)
        self.assertEquals(c.timeline.classes.first().customer, self.customer)  # should save a customer
        self.assertEquals(c.timeline.start, self.tzdatetime(2016, 8, 17, 10, 1))  # datetime for entry start should be from parameters
        self.assertEquals(c.timeline.end, self.tzdatetime(2016, 8, 17, 10, 1) + lesson.duration)  # duration should be taken from lesson

    def test_schedule_existsing_entry(self):
        """
        Create a timeline entry, that class.__get_entry should return instead of
        creating a new one
        """
        lesson = products.OrdinaryLesson.get_default()
        c = self._buy_a_lesson(lesson)
        date = self.tzdatetime(2016, 8, 17, 10, 1)
        entry = TimelineEntry(
            teacher=self.host,
            start=date,
            lesson=lesson
        )
        entry.save()
        c.schedule(
            teacher=self.host,
            date=self.tzdatetime(2016, 8, 17, 10, 1),
            allow_besides_working_hours=True,
        )
        c.save()
        self.assertEquals(c.timeline, entry)

    @override_settings(EMAIL_ASYNC=False)
    def test_schedule_email(self):
        lesson = products.OrdinaryLesson.get_default()
        c = self._buy_a_lesson(lesson)
        c.schedule(
            teacher=self.host,
            date=self.tzdatetime(2016, 8, 17, 10, 1),
            allow_besides_working_hours=True,
        )

        c.save()

        self.assertEqual(len(mail.outbox), 2)  # 1 email for the teacher and 1 email for the student
        out_emails = [outbox.to[0] for outbox in mail.outbox]

        self.assertIn(self.host.user.email, out_emails)
        self.assertIn(self.customer.user.email, out_emails)

    @override_settings(EMAIL_ASYNC=False)
    def test_cancellation_email(self):
        lesson = products.OrdinaryLesson.get_default()
        c = self._buy_a_lesson(lesson)
        with patch('market.models.class_scheduled') as scheduled_signal:
            scheduled_signal.send = MagicMock()
            c.schedule(
                teacher=self.host,
                date=self.tzdatetime(2016, 8, 17, 10, 1),
                allow_besides_working_hours=True,
            )
            c.save()
        self.assertEqual(len(mail.outbox), 0)

        c.cancel()

        self.assertEqual(len(mail.outbox), 2)  # 1 message for the teacher and 1 message for the student
        out_emails = [outbox.to[0] for outbox in mail.outbox]

        self.assertIn(self.host.user.email, out_emails)
        self.assertIn(self.customer.user.email, out_emails)

    def test_cant_automatically_schedule_lesson_that_requires_a_timeline_entry(self):
        """
        Scheduling a hosted lesson that requires a timeline entry should fail
        """
        master_class = mixer.blend(lessons.MasterClass, host=self.host)
        c = self._buy_a_lesson(master_class)

        with self.assertRaisesRegexp(CannotBeScheduled, 'timeline entry$'):
            c.schedule(
                teacher=self.host,
                date=self.tzdatetime(2016, 8, 17, 10, 1)
            )

    def test_schedule_master_class(self):
        """
        Buy a master class and then schedule it
        """
        lesson = mixer.blend(lessons.MasterClass, host=self.host)

        timeline_entry = mixer.blend(TimelineEntry,
                                     lesson=lesson,
                                     teacher=self.host,
                                     start=self.tzdatetime(2032, 12, 1)
                                     )

        timeline_entry.save()

        purchased_class = self._buy_a_lesson(lesson=lesson)
        purchased_class.save()

        purchased_class.assign_entry(timeline_entry)
        purchased_class.save()

        self.assertTrue(purchased_class.is_scheduled)
        self.assertEqual(timeline_entry.taken_slots, 1)

        purchased_class.cancel()
        self.assertEqual(timeline_entry.taken_slots, 0)

    def test_schedule_2_people_to_a_paired_lesson(self):
        customer1 = create_customer()
        customer2 = create_customer()

        paired_lesson = mixer.blend(lessons.PairedLesson, slots=2, host=self.host)

        customer1_class = Class(
            customer=customer1,
            lesson=paired_lesson
        )
        customer1_class.save()

        customer2_class = Class(
            customer=customer2,
            lesson=paired_lesson
        )
        customer2_class.save()

        timeline_entry = mixer.blend(TimelineEntry, lesson=paired_lesson, teacher=self.host, start=self.tzdatetime(2032, 12, 1))

        customer1_class.assign_entry(timeline_entry)
        customer1_class.save()

        customer2_class.assign_entry(timeline_entry)
        customer2_class.save()

        self.assertTrue(customer1_class.is_scheduled)
        self.assertTrue(customer2_class.is_scheduled)
        self.assertEqual(timeline_entry.taken_slots, 2)

        customer2_class.cancel()
        self.assertEqual(timeline_entry.taken_slots, 1)

    def test_schedule_lesson_of_a_wrong_type(self):
        """
        Try to schedule purchased master class lesson to a paired lesson event
        """
        paired_lesson = mixer.blend(lessons.PairedLesson, slots=2, host=self.host)
        paired_lesson_entry = mixer.blend(TimelineEntry, lesson=paired_lesson, teacher=self.host, active=1)

        paired_lesson_entry.save()

        purchased_class = self._buy_a_lesson(mixer.blend(lessons.MasterClass, host=self.host))
        purchased_class.save()

        with self.assertRaises(CannotBeScheduled):
            purchased_class.assign_entry(paired_lesson_entry)

        self.assertFalse(purchased_class.is_scheduled)
