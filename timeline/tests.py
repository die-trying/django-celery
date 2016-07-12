import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.utils.dateformat import format
from mixer.backend.django import mixer

from crm.models import Customer
from lessons.models import Event as LessonEvent
from timeline.models import Entry as TimelineEntry


class EntryTestCase(TestCase):
    fixtures = ('crm', 'test_timeline_entries', 'test_events')

    def setUp(self):
        self.teacher1 = mixer.blend(User, is_staff=1)
        self.teacher2 = mixer.blend(User, is_staff=1)

    def test_entry_naming(self):
        """
        Timeline entry with an assigned name should return the name of event.

        Without an event, timeline entry should return placeholder 'Usual lesson'.
        """
        event = mixer.blend(LessonEvent, name='Test_Lesson_Name', host=self.teacher1)
        entry = mixer.blend(TimelineEntry, teacher=self.teacher1, event=event)
        self.assertEqual(str(entry), 'Test_Lesson_Name')

        entry = mixer.blend(TimelineEntry, event=None)
        self.assertEqual(str(entry), 'Usual lesson')

    def test_availabe_slot_count(self):
        event = mixer.blend(LessonEvent, slots=10, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, event=event, teacher=self.teacher1)
        entry.save()

        self.assertEqual(entry.slots, 10)

    def test_taken_slot_count(self):
        event = mixer.blend(LessonEvent, slots=10, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, event=event, teacher=self.teacher1)
        entry.save()

        for i in range(0, 5):
            self.assertEqual(entry.taken_slots, i)
            test_customer = mixer.blend(Customer)

            entry.customers.add(test_customer)
            entry.save()

    def test_event_assigning(self):
        """
        Test if timeline entry takes all attributes from the event
        """
        event = mixer.blend(LessonEvent, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, event=event, teacher=self.teacher1)

        for i in ('duration', 'slots'):
            self.assertEqual(getattr(event, i), getattr(entry, i))

        self.assertEqual(entry.event_type, event.lesson_type)

    def test_is_free(self):
        """
        Schedule a customer to a timeleine entry
        """
        event = mixer.blend(LessonEvent, slots=10, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, event=event, teacher=self.teacher1)
        entry.save()

        for i in range(0, 10):
            self.assertTrue(entry.is_free)
            test_customer = mixer.blend(Customer)
            entry.customers.add(test_customer)
            entry.save()

        self.assertFalse(entry.is_free)

        """ Let's try to schedule more customers, then event allows """
        with self.assertRaises(ValidationError):
            test_customer = mixer.blend(Customer)
            entry.customers.add(test_customer)
            entry.save()

    def test_entry_without_an_event(self):
        """
        Test for a timeline entry without a direct assigned event, ex ordinary lesson
        """
        entry = mixer.blend(TimelineEntry, event=None, slots=1)
        entry.save()

        self.assertTrue(entry.is_free)

        test_customer = mixer.blend(Customer)
        entry.customers.add(test_customer)
        entry.save()

        self.assertFalse(entry.is_free)

        with self.assertRaises(ValidationError):
            test_customer = mixer.blend(Customer)
            entry.customers.add(test_customer)
            entry.save()

    def test_assign_entry_to_a_different_teacher(self):
        """
        We should not have possibility to assign an event with different host
        to someones timeline entry
        """
        event = mixer.blend(LessonEvent, host=self.teacher1)

        with self.assertRaises(ValidationError):
            entry = mixer.blend(TimelineEntry, teacher=self.teacher2, event=event)
            entry.save()


class FunctionalEntryTest(TestCase):
    """
    Generate dummy teachers timeline and fetch it through JSON
    """
    def setUp(self):
        """
        Calendar administration is limited to staff members, so we login
        with a super user here.
        """
        self.user = User.objects.create_superuser('test', 'te@ss.tt', 'Chug6ATh9hei')
        self.c = Client()
        self.c.login(username='test', password='Chug6ATh9hei')

    def test_user_json(self):
        duration = timedelta(minutes=71)
        teacher = mixer.blend(User, is_staff=1)
        teacher.save()

        mocked_entries = {}
        for i in range(0, 10):
            entry = mixer.blend(TimelineEntry, teacher=teacher, duration=duration)
            mocked_entries[entry.pk] = entry

        response = self.c.get('/timeline/%s.json' % teacher.username)
        data = json.loads(response.content.decode('utf-8'))

        for i in data:
            id = i['entry']['id']
            mocked_entry = mocked_entries[id]

            self.assertEqual(i['teacher']['username'], teacher.username)

            self.assertEqual(i['entry']['start'],
                             format(mocked_entry.start_time, 'c')
                             )
            self.assertEqual(i['entry']['end'],
                             format(mocked_entry.start_time + duration, 'c')
                             )
