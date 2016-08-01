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
        response = self.c.get('/teachers/2032-05-03/type/100500/teachers.json')
        print(response.content)
        self.assertEqual(response.status_code, 404)  # non-existent lesson_type

        response = self.c.get('/teachers/2032-05-03/type/100500/lessons.json')
        self.assertEqual(response.status_code, 404)  # non-existent lesson_id

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

        response = self.c.get('/teachers/2032-05-06/type/%d/teachers.json' % master_class_type.pk)
        self.assertEquals(response.status_code, 200)

        teachers = json.loads(response.content.decode('utf-8'))
        self.assertEquals(len(teachers), 2)
        self.assertEquals(len(teachers[0]['slots']), 1)

        self.assertEquals(teachers[0]['slots'][0], '14:10')
        self.assertEquals(teachers[1]['slots'][0], '14:15')
