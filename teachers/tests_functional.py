import json
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import ClientTestCase, create_teacher
from teachers.models import WorkingHours
from timeline.models import Entry as TimelineEntry


class TestWorkingHours(ClientTestCase):
    def setUp(self):
        self.teacher = create_teacher()
        super().setUp()

    def test_hours(self):
        """
        Test for generated json with teacher's working hours.
        """
        mocked_hours = {}

        for i in range(0, 7):
            hours = mixer.blend(WorkingHours, teacher=self.teacher, weekday=i)
            hours.save()
            mocked_hours[hours.pk] = hours
            print(hours)

        response = self.c.get('/teachers/%s/hours.json' % self.teacher.user.username)
        self.assertEquals(response.status_code, 200)

        got_hours = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(got_hours), 7)

        for i in got_hours:
            id = i['id']
            got_mocked_hours = mocked_hours[id]
            self.assertEqual(i['weekday'], got_mocked_hours.weekday)
            self.assertEqual(i['start'], str(got_mocked_hours.start))
            self.assertEqual(i['end'], str(got_mocked_hours.end))


class TestSlotsJson(ClientTestCase):
    """
    Getting time slots of distinct teacher
    """
    def setUp(self):
        self.teacher = create_teacher()
        mixer.blend(WorkingHours, teacher=self.teacher, weekday=0, start='13:00', end='15:00')  # monday
        mixer.blend(WorkingHours, teacher=self.teacher, weekday=1, start='17:00', end='19:00')  # thursday

        super().setUp()

    def test_404(self):
        response = self.c.get('/teachers/%s/2032-05-05/slots.json' % self.teacher.user.username)  # wednesday
        self.assertEqual(response.status_code, 404)  # our teacher does not work on wednesdays

        response = self.c.get('/teachers/%s/2032-05-03/slots.json?lesson_type=100500' % self.teacher.user.username)
        self.assertEqual(response.status_code, 404)  # non-existent lesson_type

        response = self.c.get('/teachers/%s/2032-05-03/slots.json?lesson_id=100500' % self.teacher.user.username)
        self.assertEqual(response.status_code, 404)  # non-existent lesson_id

    def test_all_slots(self):
        response = self.c.get('/teachers/%s/2032-05-03/slots.json' % self.teacher.user.username)  # monday
        self.assertEqual(response.status_code, 200)

        response = json.loads(response.content.decode('utf-8'))
        slots = response[0]['slots']
        self.assertEquals(len(slots), 4)
        self.assertEquals(slots[0], '13:00')
        self.assertEquals(slots[-1], '14:30')

    def test_filter_by_lesson_type(self):
        master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        entry = TimelineEntry(teacher=self.teacher,
                              lesson=master_class,
                              start=datetime(2032, 5, 6, 14, 10),
                              end=datetime(2032, 5, 6, 14, 40)
                              )
        entry.save()
        master_class_type = ContentType.objects.get_for_model(master_class)

        response = self.c.get(
            '/teachers/%s/2032-05-06/slots.json?lesson_type=%d' % (self.teacher.user.username, master_class_type.pk)
        )
        self.assertEquals(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        slots = response[0]['slots']
        self.assertEquals(len(slots), 1)
        self.assertEquals(slots[0], '14:10')

    def test_filter_by_lesson(self):
        master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        entry = TimelineEntry(teacher=self.teacher,
                              lesson=master_class,
                              start=datetime(2032, 5, 6, 14, 10),
                              end=datetime(2032, 5, 6, 14, 40)
                              )
        entry.save()

        response = self.c.get(
            '/teachers/%s/2032-05-06/slots.json?lesson_id=%d' % (self.teacher.user.username, master_class.pk)
        )
        self.assertEquals(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        slots = response[0]['slots']
        self.assertEquals(len(slots), 1)
        self.assertEquals(slots[0], '14:10')


class testTeacherSlotsJSON(ClientTestCase):
    """
    Getting timeslots of any available teacher.

    We do not test getting teacher for particular lesson, because frontend should
    use teacher_slots view when it knows the particular teacher.
    """
    def setUp(self):
        self.first_teacher = create_teacher()
        mixer.blend(WorkingHours, teacher=self.first_teacher, weekday=0, start='13:00', end='15:00')  # monday
        mixer.blend(WorkingHours, teacher=self.first_teacher, weekday=1, start='17:00', end='19:00')  # thursday

        self.second_teacher = create_teacher()
        mixer.blend(WorkingHours, teacher=self.second_teacher, weekday=0, start='13:00', end='15:00')  # monday
        mixer.blend(WorkingHours, teacher=self.second_teacher, weekday=4, start='17:00', end='19:00')  # thursday

        super().setUp()

    def test_404(self):
        response = self.c.get('/teachers/2032-05-05/slots.json')  # wednesday
        self.assertEqual(response.status_code, 404)  # no one works on wednesdays

        response = self.c.get('/teachers/2032-05-03/slots.json?lesson_type=100500')
        self.assertEqual(response.status_code, 404)  # non-existent lesson_type

        response = self.c.get('/teachers/2032-05-03/slots.json?lesson_id=100500')
        self.assertEqual(response.status_code, 404)  # non-existent lesson_id

    def test_all_slots(self):
        response = self.c.get('/teachers/2032-05-03/slots.json')  # monday, 2 teachers
        self.assertEqual(response.status_code, 200)

        teachers = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(teachers), 2)
        self.assertEqual(len(teachers[0]['slots']), 4)

        self.assertEqual(teachers[0]['name'], str(self.first_teacher.user.crm))
        self.assertEqual(teachers[0]['slots'][0], '13:00')
        self.assertEqual(teachers[0]['slots'][-1], '14:30')

    def test_filter_by_lesson_type(self):
        first_master_class = mixer.blend(lessons.MasterClass, host=self.first_teacher)
        second_master_class = mixer.blend(lessons.MasterClass, host=self.second_teacher)
        entry = TimelineEntry(teacher=self.first_teacher,
                              lesson=first_master_class,
                              start=datetime(2032, 5, 6, 14, 10),
                              end=datetime(2032, 5, 6, 14, 40)
                              )
        entry.save()
        entry = TimelineEntry(teacher=self.second_teacher,
                              lesson=second_master_class,
                              start=datetime(2032, 5, 6, 14, 15),
                              end=datetime(2032, 5, 6, 14, 45)
                              )
        entry.save()
        master_class_type = ContentType.objects.get_for_model(first_master_class)

        response = self.c.get('/teachers/2032-05-06/slots.json?lesson_type=%d' % master_class_type.pk)
        self.assertEquals(response.status_code, 200)

        teachers = json.loads(response.content.decode('utf-8'))
        self.assertEquals(len(teachers), 2)
        self.assertEquals(len(teachers[0]['slots']), 1)

        self.assertEquals(teachers[0]['slots'][0], '14:10')
        self.assertEquals(teachers[1]['slots'][0], '14:15')
