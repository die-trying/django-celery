import iso8601
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from mixer.backend.django import mixer

import lessons.models as lessons
from crm.models import Customer
from teachers.models import Teacher
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

    def test_default_scope(self):
        active_lesson = mixer.blend(lessons.OrdinaryLesson, name='Active_lesson')
        inactive_lesson = mixer.blend(lessons.OrdinaryLesson, name='Inactive_lesson')

        active_entry = mixer.blend(TimelineEntry, teacher=self.teacher1, lesson=active_lesson, active=1)
        inactive_entry = mixer.blend(TimelineEntry, teacher=self.teacher1, lesson=inactive_lesson, active=0)

        active_pk = active_entry.pk
        inactive_pk = inactive_entry.pk

        entries = TimelineEntry.objects.all().values_list('id', flat=True)
        self.assertIn(active_pk, entries)
        self.assertNotIn(inactive_pk, entries)

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


class SlotAvailableTest(TestCase):
    def setUp(self):
        self.teacher = mixer.blend(User, is_staff=1)
        self.teacher.teacher_data = mixer.blend(Teacher)

        self.lesson = mixer.blend(lessons.OrdinaryLesson, teacher=self.teacher)

        self.big_entry = mixer.blend(TimelineEntry,
                                     teacher=self.teacher,
                                     start=iso8601.parse_date('2016-01-02 18:00'),
                                     end=iso8601.parse_date('2016-01-03 12:00'),
                                     )

    def test_can_be_created(self):
        """
        Create two entries — one overlapping with the big_entry, and one — not
        """
        overlapping_entry = TimelineEntry(teacher=self.teacher,
                                          start=iso8601.parse_date('2016-01-03 04:00'),
                                          end=iso8601.parse_date('2016-01-03 04:30'),
                                          )
        self.assertTrue(overlapping_entry.is_overlapping())

        non_overlapping_entry = TimelineEntry(teacher=self.teacher,
                                              start=iso8601.parse_date('2016-01-03 12:00'),
                                              end=iso8601.parse_date('2016-01-03 12:30'),
                                              )
        self.assertFalse(non_overlapping_entry.is_overlapping())

    def test_overlapping_with_different_teacher(self):
        """
        Check, if it's pohuy, that an entry overlapes entry of the other teacher
        """
        other_teacher = mixer.blend(User, is_staff=1)
        test_entry = TimelineEntry(teacher=other_teacher,
                                   start=iso8601.parse_date('2016-01-03 04:00'),
                                   end=iso8601.parse_date('2016-01-03 04:30'),
                                   )
        self.assertFalse(test_entry.is_overlapping())

    def test_cant_save(self):
        """
        We should not have posibillity to save a timeline entry, that can not
        be created
        """
        overlapping_entry = TimelineEntry(teacher=self.teacher,
                                          lesson=self.lesson,
                                          start=iso8601.parse_date('2016-01-03 04:00'),
                                          end=iso8601.parse_date('2016-01-03 04:30'),
                                          allow_overlap=False,  # excplicitly say, that entry can't overlap other ones
                                          )
        with self.assertRaises(ValidationError):
            overlapping_entry.save()


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
