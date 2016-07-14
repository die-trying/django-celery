import json
from datetime import timedelta

import iso8601
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.utils.dateformat import format
from mixer.backend.django import mixer

import lessons.models as lessons
from crm.models import Customer
from elk.utils import date
from timeline.models import Entry as TimelineEntry


class EntryTestCase(TestCase):
    fixtures = ('crm',)

    def setUp(self):
        self.teacher1 = mixer.blend(User, is_staff=1)
        self.teacher2 = mixer.blend(User, is_staff=1)

    def test_entry_naming(self):
        """
        Timeline entry with an assigned name should return the name of event.

        Without an event, timeline entry should return placeholder 'Usual lesson'.
        """
        lesson = mixer.blend(lessons.OrdinaryLesson, name='Test_Lesson_Name')
        entry = mixer.blend(TimelineEntry, teacher=self.teacher1, lesson=lesson)
        self.assertEqual(str(entry), 'Test_Lesson_Name')

    def test_availabe_slot_count(self):
        event = mixer.blend(lessons.MasterClass, slots=10, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, lesson=event, teacher=self.teacher1)
        entry.save()

        self.assertEqual(entry.slots, 10)

    def test_taken_slot_count(self):
        event = mixer.blend(lessons.MasterClass, slots=10, host=self.teacher1)
        entry = mixer.blend(TimelineEntry, lesson=event, teacher=self.teacher1)
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
        lesson = mixer.blend(lessons.OrdinaryLesson)
        entry = mixer.blend(TimelineEntry, lesson=lesson, teacher=self.teacher1)

        for i in ('duration', 'slots'):
            self.assertEqual(getattr(lesson, i), getattr(entry, i))

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
            test_customer = mixer.blend(Customer)
            entry.customers.add(test_customer)
            entry.save()

        self.assertFalse(entry.is_free)

        """ Let's try to schedule more customers, then event allows """
        with self.assertRaises(ValidationError):
            test_customer = mixer.blend(Customer)
            entry.customers.add(test_customer)
            entry.save()

    def test_assign_entry_to_a_different_teacher(self):
        """
        We should not have possibility to assign an event with different host
        to someones timeline entry
        """
        lesson = mixer.blend(lessons.MasterClass, host=self.teacher1)

        with self.assertRaises(ValidationError):
            entry = mixer.blend(TimelineEntry, teacher=self.teacher2, lesson=lesson)
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
            entry = mixer.blend(TimelineEntry, teacher=teacher, duration=duration, start_time=date.ago(days=5))
            mocked_entries[entry.pk] = entry

        response = self.c.get('/timeline/%s.json' % teacher.username)

        for i in json.loads(response.content.decode('utf-8')):
            id = i['id']
            mocked_entry = mocked_entries[id]

            self.assertEqual(i['start'],
                             format(mocked_entry.start_time, 'c')
                             )
            self.assertEqual(i['end'],
                             format(mocked_entry.start_time + duration, 'c')
                             )

    def test_user_json_filter(self):
        x = iso8601.parse_date('2016-01-01')
        teacher = mixer.blend(User, is_staff=1)
        for i in range(0, 10):
            entry = mixer.blend(TimelineEntry, teacher=teacher, start_time=x)
            x += timedelta(days=1)
            print(x.__class__)
            entry.save()

        response = self.c.get('/timeline/%s.json?start=2013-01-01&end=2016-01-03' % teacher.username)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)


class PermissionTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('superuser', 'te@ss.a', '123')
        self.user = User.objects.create_user('user', 'te@ss.tt', '123')

        self.c = Client()

        self.teacher = mixer.blend(User, is_staff=1)

    def test_create_form_permission(self):
        self.c.login(username='user', password='123')
        response = self.c.get('/timeline/%s/create/' % self.teacher.username)
        self.assertNotEqual(response.status_code, 200)

        self.c.logout()

        self.c.login(username='superuser', password='123')
        response = self.c.get('/timeline/%s/create/' % self.teacher.username)
        self.assertEqual(response.status_code, 200)
