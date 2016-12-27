from datetime import timedelta
from unittest.mock import MagicMock

import icalendar
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import override_settings
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import ClassIntegrationTestCase, TestCase, create_customer, create_teacher
from lessons import models as lessons
from market.models import Class
from timeline.models import Entry as TimelineEntry


@freeze_time('2005-05-03 12:41')
class EntryTestCase(TestCase):
    fixtures = ('crm',)

    def setUp(self):
        self.teacher1 = create_teacher(works_24x7=True)
        self.teacher2 = create_teacher(works_24x7=True)

    def test_entry_naming_with_student(self):
        lesson = mixer.blend(lessons.OrdinaryLesson, name='Test_Lesson_Name')
        entry = mixer.blend(TimelineEntry, teacher=self.teacher1, lesson=lesson, start=self.tzdatetime(2016, 2, 6, 3, 0))
        customer = create_customer()
        c = Class(
            customer=customer,
            lesson_type=lesson.get_contenttype(),
        )
        c.assign_entry(entry)
        c.save()
        entry.refresh_from_db()
        self.assertIn(customer.full_name, str(entry))

    def test_availabe_slot_count(self):
        event = mixer.blend(lessons.MasterClass, slots=10, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, lesson=event, teacher=self.teacher1)
        entry.save()

        self.assertEqual(entry.slots, 10)

    def test_event_assigning(self):
        """
        Test if timeline entry takes all attributes from the event
        """
        lesson = mixer.blend(lessons.OrdinaryLesson)
        entry = mixer.blend(TimelineEntry, lesson=lesson, teacher=self.teacher1)

        self.assertEqual(entry.slots, lesson.slots)
        self.assertEqual(entry.end, entry.start + lesson.duration)

        self.assertEqual(entry.lesson_type, ContentType.objects.get(app_label='lessons', model='ordinarylesson'))

    def test_is_free(self):
        """
        Schedule a customer to a timeleine entry
        """
        lesson = mixer.blend(lessons.MasterClass, slots=10, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, lesson=lesson, teacher=self.teacher1)
        entry.save()

        for i in range(0, 10):
            self.assertTrue(entry.is_free)
            self.assertEqual(entry.taken_slots, i)  # by the way let's test taken_slots count
            customer = create_customer()
            c = mixer.blend(Class, lesson_type=lesson.get_contenttype(), customer=customer)
            entry.classes.add(c)  # please don't use it in your code! use :model:`market.Class`.assign_entry() instead
            entry.save()

        self.assertFalse(entry.is_free)

        """ Let's try to schedule more customers, then event allows """
        with self.assertRaises(ValidationError):
            customer = create_customer()
            c = mixer.blend(Class, lesson_type=lesson.get_contenttype(), customer=customer)
            entry.classes.add(c)  # please don't use it in your code! use :model:`market.Class`.assign_entry() instead
            entry.save()

    def test_as_ical(self):
        """
        Test ical representation
        """
        lesson = mixer.blend(lessons.MasterClass, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, lesson=lesson, teacher=self.teacher1)
        ical = icalendar.Calendar.from_ical(entry.as_ical())

        ev = ical.walk('VEVENT')[0]

        self.assertEqual(ev['dtstart'].dt, entry.start)
        self.assertEqual(ev['dtend'].dt, entry.end)

    def test_is_ical_title(self):
        """
        Ensure that calendar event has title from TimelineEntry.event_title()
        """
        entry = mixer.blend(TimelineEntry, teacher=self.teacher1)
        entry.event_title = MagicMock(return_value='tstttl')
        ical = icalendar.Calendar.from_ical(entry.as_ical())
        ev = ical.walk('VEVENT')[0]

        self.assertEqual(str(ev['summary']), 'tstttl')

    def test_assign_entry_to_a_different_teacher(self):
        """
        We should not have possibility to assign an event with different host
        to someones timeline entry
        """
        lesson = mixer.blend(lessons.MasterClass, host=self.teacher1)

        with self.assertRaises(ValidationError):
            entry = mixer.blend(TimelineEntry, teacher=self.teacher2, lesson=lesson)
            entry.save()

    @freeze_time('2005-05-03 12:41')
    def test_entry_in_past(self):
        lesson = mixer.blend(lessons.MasterClass, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, teacher=self.teacher1, lesson=lesson, start=self.tzdatetime(2002, 1, 2, 3, 0))
        self.assertTrue(entry.has_finished())

        entry.start = self.tzdatetime(2032, 12, 1)
        entry.end = entry.start + timedelta(minutes=30)
        entry.save()
        self.assertFalse(entry.has_finished())

    def test_to_be_marked_as_finished_queryset(self):
        lesson = mixer.blend(lessons.MasterClass, host=self.teacher1, duration='01:00:00')
        mixer.blend(TimelineEntry, teacher=self.teacher1, lesson=lesson, start=self.tzdatetime(2016, 12, 15, 15, 14))

        with freeze_time('2016-12-20 17:15'):
            self.assertEqual(TimelineEntry.objects.to_be_marked_as_finished().count(), 1)

        with freeze_time('2016-12-15 15:13'):
            self.assertEqual(TimelineEntry.objects.to_be_marked_as_finished().count(), 0)  # two minutes in past this entry shoud not be marked as finished

    def test_dont_automaticaly_mark_finished_entries_as_finished_one_more_time(self):
        lesson = mixer.blend(lessons.MasterClass, host=self.teacher1, duration='01:00:00')
        entry = mixer.blend(TimelineEntry, teacher=self.teacher1, lesson=lesson, start=self.tzdatetime(2016, 12, 15, 15, 14))

        with freeze_time('2016-12-15 17:15'):
            entry.is_finished = True
            entry.save()
            self.assertEqual(TimelineEntry.objects.to_be_marked_as_finished().count(), 0)

    def test_get_step2_url(self):
        lesson = mixer.blend(lessons.MasterClass, host=self.teacher1, duration='01:00:00')
        entry = mixer.blend(
            TimelineEntry,
            teacher=self.teacher1,
            lesson=lesson,
            start=self.tzdatetime(2016, 12, 15, 11, 32)
        )
        step2_url = entry.get_step2_url()

        self.assertIn('/{}/{}/2016-12-15/11:32/'.format(self.teacher1.pk, lesson.get_contenttype().pk), step2_url)

    @override_settings(TIME_ZONE='Europe/Moscow')
    def test_step2_url_localizes_time(self):
        """
        Check if Entry.get_step2_url() returns time in local format for user
        """
        entry = mixer.blend(
            TimelineEntry,
            teacher=self.teacher1,
            lesson=mixer.blend(lessons.MasterClass, host=self.teacher1, duration='01:00:00'),
            start=self.tzdatetime('UTC', 2016, 12, 15, 20, 32)
        )
        step2_url = entry.get_step2_url()
        self.assertIn('2016-12-15/15:32', step2_url)


class TestEntryTitle(ClassIntegrationTestCase):
    def test_customer_single_lesson(self):
        self.lesson = lessons.OrdinaryLesson.get_default()

        c = self._buy_a_lesson()
        entry = self._create_entry()
        self._schedule(c, entry)

        title = c.timeline.event_title()  # we use `c.timeline` instead of `entry` because scheduling has created another timeline entry and our entry is invalid now

        self.assertIn('Single lesson', title)
        self.assertIn('with %s' % self.host.user.crm.first_name, title)

    def test_customer_hosted_lesson(self):
        self.lesson = mixer.blend(lessons.MasterClass, name='Test Lesson Name', host=self.host, slots=5)

        entry = self._create_entry()
        entry.slots = 5
        entry.save()
        c = self._buy_a_lesson()
        self._schedule(c, entry)

        title = entry.event_title()

        self.assertIn('Test Lesson Name', title)
        self.assertIn('with %s' % self.host.user.crm.first_name, title)

    def test_teacher_single_lesson(self):
        self.lesson = lessons.OrdinaryLesson.get_default()

        c = self._buy_a_lesson()
        entry = self._create_entry()
        self._schedule(c, entry)

        title = str(c.timeline)  # we use `c.timeline` instead of `entry` because scheduling has created another timeline entry and our entry is invalid now

        self.assertEqual(title, self.customer.full_name)

    def test_teacher_hosted_Lesson(self):
        self.lesson = mixer.blend(lessons.MasterClass, internal_name='Test Lesson Name', host=self.host, slots=5)

        entry = self._create_entry()
        entry.slots = 5
        entry.save()
        c = self._buy_a_lesson()
        self._schedule(c, entry)

        self.customer = create_customer()  # create another customer
        c = self._buy_a_lesson()
        self._schedule(c, entry)

        entry.refresh_from_db()  # entry should update slot count from the database

        title = str(entry)

        self.assertEqual(title, 'Test Lesson Name 2/5')

    def test_teacher_hosted_lesson_without_customers(self):
        self.lesson = mixer.blend(lessons.MasterClass, internal_name='Test Lesson Name', host=self.host, slots=5)
        entry = self._create_entry()

        title = str(entry)

        self.assertEqual(title, 'Test Lesson Name')
