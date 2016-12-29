import json
from datetime import datetime, timedelta

from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import ClientTestCase, create_teacher
from lessons import models as lessons
from market.models import Class
from teachers.models import WorkingHours
from timeline.models import Entry as TimelineEntry


@freeze_time('2032-05-01 12:30')
class SchdulingPopupSlotsTestCase(ClientTestCase):
    """
    Simple test suit for testing JSON api, required for scheduling
    popup. Popup queries free slots as lessons (for hosted lessons
    i.e. master classes) and as teachers.
    """
    @classmethod
    def setUpTestData(cls):
        """
        Create two teachers with different working hours
        """
        cls.first_teacher = create_teacher()
        cls.first_teacher.user.last_name = 'A_first'  # for correct ordering
        cls.first_teacher.user.save()
        mixer.blend(WorkingHours, teacher=cls.first_teacher, weekday=0, start='13:00', end='15:30')  # monday
        mixer.blend(WorkingHours, teacher=cls.first_teacher, weekday=1, start='17:00', end='19:00')  # thursday

        cls.second_teacher = create_teacher()
        cls.second_teacher.user.last_name = 'B_second'  # for correct ordering
        cls.second_teacher.user.save()
        mixer.blend(WorkingHours, teacher=cls.second_teacher, weekday=0, start='13:00', end='15:00')  # monday
        mixer.blend(WorkingHours, teacher=cls.second_teacher, weekday=4, start='17:00', end='19:00')  # thursday

    def _buy_a_lesson(self, lesson):
            c = Class(
                customer=self.customer,
                lesson=lesson
            )
            c.save()
            return c

    def test_404(self):
        response = self.c.get('/market/2032-05-03/type/100500/records.json')
        self.assertEqual(response.status_code, 404)  # non-existent lesson_type

        response = self.c.get('/market/2032-05-03/type/100500/lessons.json')
        self.assertEqual(response.status_code, 404)  # non-existent lesson_id

        response = self.c.get('/market/2032-05-03/type/%s/lessons.json' % lessons.MasterClass.get_contenttype().pk)
        self.assertEqual(response.status_code, 404)  # there are no lessons planned

    def test_filter_by_lesson_type(self):
        first_master_class = mixer.blend(lessons.MasterClass, host=self.first_teacher)
        second_master_class = mixer.blend(lessons.MasterClass, host=self.second_teacher)
        entry = TimelineEntry(teacher=self.first_teacher,
                              lesson=first_master_class,
                              start=datetime(2032, 5, 6, 14, 10),
                              end=datetime(2032, 5, 6, 14, 40),
                              )
        entry.save()
        entry = TimelineEntry(teacher=self.second_teacher,
                              lesson=second_master_class,
                              start=datetime(2032, 5, 6, 14, 15),
                              end=datetime(2032, 5, 6, 14, 45),
                              )
        entry.save()
        master_class_type = ContentType.objects.get_for_model(first_master_class)

        response = self.c.get('/market/2032-05-06/type/%d/lessons.json' % master_class_type.pk)
        self.assertEquals(response.status_code, 200)

        records = json.loads(response.content.decode('utf-8'))
        self.assertEquals(len(records), 2)
        self.assertEquals(len(records[0]['slots']), 1)

        self.assertIsTime(records[0]['slots'][0]['server'])  # assert that returned slots carry some time (we dont care about timezones here)
        self.assertIsTime(records[1]['slots'][0]['server'])

        self.assertEquals(records[0]['name'], first_master_class.name)
        self.assertEquals(records[1]['name'], second_master_class.name)

        self.assertEquals(records[0]['host'], self.first_teacher.user.crm.full_name)
        self.assertEquals(records[1]['host'], self.second_teacher.user.crm.full_name)

    def test_filter_by_lesson_type_timezone(self):
        """
        Create 24 master classes and make sure they are accessible in the same timezone
        """
        master_class = mixer.blend(lessons.MasterClass, host=self.first_teacher)
        start = self.tzdatetime('Europe/Moscow', 2032, 5, 3, 0, 0)
        for i in range(0, 24):
            mixer.blend(
                TimelineEntry,
                lesson=master_class,
                teacher=self.first_teacher,
                start=start,
                end=start + timedelta(hours=1)
            )
            start += timedelta(hours=1)

        self.c.login(username=self.superuser_login, password=self.superuser_password)  # need to login once again due to timezone change
        response = self.c.get('/market/2032-05-03/type/%d/lessons.json' % lessons.MasterClass.get_contenttype().pk)

        self.assertEquals(response.status_code, 200)
        records = json.loads(response.content.decode('utf-8'))
        self.assertEquals(len(records), 1)
        self.assertEquals(len(records[0]['slots']), 24)

    @override_settings(TIME_ZONE='Europe/Moscow')
    def test_filter_by_date(self):
        response = self.c.get('/market/2032-05-03/type/%d/teachers.json' % lessons.OrdinaryLesson.get_contenttype().pk)
        self.assertEquals(response.status_code, 200)

        records = json.loads(response.content.decode('utf-8'))

        self.assertEquals(len(records), 2)
        self.assertEquals(len(records[0]['slots']), 5)  # this first teacher works till 15:30
        self.assertEquals(len(records[1]['slots']), 4)  # and the second works till 15:00

        self.assertIsTime(records[0]['slots'][-1]['server'])
        self.assertIsTime(records[1]['slots'][-1]['server'])

        self.assertEquals(records[0]['name'], self.first_teacher.user.crm.full_name)
        self.assertEquals(records[1]['name'], self.second_teacher.user.crm.full_name)

        self.assertNotIn('host', records[0].keys())
        self.assertNotIn('host', records[1].keys())  # records here represent teachers, so don't need any host information
