import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from mixer.backend.django import mixer

from teachers.models import Teacher, WorkingHours


class TestFreeSlots(TestCase):
    def setUp(self):
        self.teacher = mixer.blend(Teacher)
        mixer.blend(WorkingHours, teacher=self.teacher, weekday=0, start='13:00', end='15:00')  # monday
        mixer.blend(WorkingHours, teacher=self.teacher, weekday=1, start='17:00', end='19:00')  # thursday

    def test_working_hours_for_date(self):
        """
        Get datetime.datetime objects for start working hours and end working hours
        """
        working_hours_monday = WorkingHours.for_date(teacher=self.teacher, date='2016-07-18')
        self.assertIsNotNone(working_hours_monday)
        self.assertEqual(working_hours_monday.start.strftime('%Y-%m-%d %H:%M'), '2016-07-18 13:00')
        self.assertEqual(working_hours_monday.end.strftime('%Y-%m-%d %H:%M'), '2016-07-18 15:00')

        working_hours_wed = WorkingHours.for_date(teacher=self.teacher, date='2016-07-20')
        self.assertIsNone(working_hours_wed)  # should not throw DoesNotExist

    def test_get_free_slots(self):
        """
        Simple unit test for fetching free slots
        """
        slots = self.teacher.find_free_slots(date='2016-07-18')
        self.assertEquals(len(slots), 4)

        def time(slot):
            return slot.strftime('%H:%M')

        self.assertEqual(time(slots[0]), '13:00')
        self.assertEqual(time(slots[-1]), '14:30')

        slots = self.teacher.find_free_slots(date='2016-07-18', period=timedelta(minutes=20))
        self.assertEquals(len(slots), 6)
        self.assertEqual(time(slots[0]), '13:00')
        self.assertEqual(time(slots[1]), '13:20')
        self.assertEqual(time(slots[-1]), '14:40')

        slots = self.teacher.find_free_slots(date='2016-07-20')
        self.assertIsNone(slots)  # should not throw DoesNotExist


class TestTeachers(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_superuser('test', 'te@ss.tt', '123')
        self.user.teacher_data = mixer.blend(Teacher, user=self.user)
        self.c.login(username='test', password='123')

    def test_hours_JSON(self):
        """
        Test for generated json with teacher's working hours.
        """
        mocked_hours = {}

        for i in range(0, 7):
            hours = mixer.blend(WorkingHours, teacher=self.user.teacher_data, weekday=i)
            hours.save()
            mocked_hours[hours.pk] = hours
            print(hours)

        response = self.c.get('/teachers/%s/hours.json' % self.user.username)
        self.assertEquals(response.status_code, 200)

        got_hours = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(got_hours), 7)

        for i in got_hours:
            id = i['id']
            got_mocked_hours = mocked_hours[id]
            self.assertEqual(i['weekday'], got_mocked_hours.weekday)
            self.assertEqual(i['start'], str(got_mocked_hours.start))
            self.assertEqual(i['end'], str(got_mocked_hours.end))
