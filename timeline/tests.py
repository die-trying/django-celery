from django.test import TestCase
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer


from crm.models import Customer
from timeline.models import Entry as TimelineEntry
from lessons.models import Event as LessonEvent
from django.contrib.auth.models import User


class EntryTestCase(TestCase):
    fixtures = ('crm', 'test_timeline_entries', 'test_events')

    def setUp(self):
        self.teacher1 = mixer.blend(User, is_staff=1)
        self.teacher2 = mixer.blend(User, is_staff=1)

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

    def test_is_free(self):
        event = mixer.blend(LessonEvent, slots=10, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, event=event, teacher=self.teacher1)
        entry.save()

        self.assertTrue(entry.is_free)

        for i in range(0, 10):
            test_customer = mixer.blend(Customer)
            entry.customers.add(test_customer)
            entry.save()

        self.assertFalse(entry.is_free)

        with self.assertRaises(ValidationError):
            test_customer = mixer.blend(Customer)
            entry.customers.add(test_customer)
            entry.save()

    def test_assign_entry_to_a_different_teacher(self):
        event = mixer.blend(LessonEvent, teacher=self.teacher1)

        with self.assertRaises(ValidationError):
            entry = mixer.blend(TimelineEntry, teacher=self.teacher2, event=event)
            entry.save()
