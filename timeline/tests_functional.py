import json
from datetime import datetime, timedelta

from django.contrib.contenttypes.models import ContentType
from django.utils.dateparse import parse_date, parse_datetime
from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import ClientTestCase, create_teacher
from teachers.models import WorkingHours
from timeline.models import Entry as TimelineEntry


class EntryCRUDTest(ClientTestCase):
    def setUp(self):
        self.teacher = create_teacher()
        self.lesson = mixer.blend(lessons.OrdinaryLesson, duration=timedelta(minutes=33))
        self.lesson_type = ContentType.objects.get_for_model(lessons.OrdinaryLesson).pk

        super().setUp()

    def testCRUD(self):
        self._create()
        self._update()
        self._delete()

    def _create(self):
        response = self.c.post('/timeline/%s/create/' % self.teacher.user.username, {
            'lesson_type': self.lesson_type,
            'lesson_id': self.lesson.pk,
            'teacher': self.teacher.pk,
            'start_0': '06/29/2016',
            'start_1': '15:00',
            'duration': '00:33',
        })
        self.assertEqual(response.status_code, 302)

        self.added_entry = self.__get_entry_from()

        end = parse_datetime(self.added_entry['end']).replace(tzinfo=None)
        self.assertEqual(end, parse_datetime('2016-06-29 15:33:00'))
        self.assertEqual(self.added_entry['title'], self.lesson.name)

        entry = TimelineEntry.objects.get(pk=self.added_entry['id'])
        self.assertIsNotNone(entry)

    def _update(self):
        pk = self.added_entry['id']

        response = self.c.post('/timeline/%s/%d/update/' % (self.teacher.user.username, pk), {
            'lesson_type': self.lesson_type,
            'lesson_id': self.lesson.pk,
            'teacher': self.teacher.pk,
            'start_0': '06/29/2016',
            'start_1': '16:00',  # moved fwd for 1 hour
            'duration': '00:33',
        })
        self.assertEqual(response.status_code, 302)

        self.added_entry = self.__get_entry_from()

        end = parse_datetime(self.added_entry['end']).replace(tzinfo=None)
        self.assertEqual(end, parse_datetime('2016-06-29 16:33:00'))
        self.assertEqual(self.added_entry['title'], self.lesson.name)

    def _delete(self):
        pk = self.added_entry['id']
        response = self.c.get('/timeline/%s/%d/update/' % (self.teacher.user.username, pk))
        self.assertEqual(response.status_code, 200, 'Should generate an edit form')

        with self.assertHTML(response, 'a.text-danger') as (delete_link,):
            delete_link = delete_link.attrib.get('href')
            response = self.c.get(delete_link)
            self.assertEqual(response.status_code, 302)

            with self.assertRaises(TimelineEntry.DoesNotExist):  # should be deleted now
                TimelineEntry.objects.get(pk=pk)

    def __get_entry_from(self):
        response = self.c.get('/timeline/%s.json?start=2016-06-28&end=2016-06-30' % self.teacher.user.username)
        self.assertEqual(response.status_code, 200)
        entries = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(entries), 1)

        return entries[0]


class EntryAPITest(ClientTestCase):
    """
    Generate dummy teachers timeline and fetch it through JSON
    """
    def setUp(self):
        """
        Calendar administration is limited to staff members, so we login
        with a super user here.
        """
        self.teacher = create_teacher()

        super().setUp()

    def test_create_user(self):
        duration = timedelta(minutes=71)

        mocked_entries = {}

        now = datetime.now()
        for i in range(0, 10):
            entry = mixer.blend(TimelineEntry,
                                teacher=self.teacher,
                                start=(now - timedelta(days=3)),
                                end=(now + duration),
                                )
            mocked_entries[entry.pk] = entry
            print(entry.start, entry.end)

        response = self.c.get('/timeline/%s.json' % self.teacher.user.username)

        for i in json.loads(response.content.decode('utf-8')):
            id = i['id']
            mocked_entry = mocked_entries[id]

            start = parse_datetime(i['start']).replace(tzinfo=None)
            end = parse_datetime(i['end']).replace(tzinfo=None)
            self.assertEqual(start, mocked_entry.start)
            self.assertEqual(end, now + duration)

    def test_create_user_filter(self):
        x = parse_date('2016-01-01')
        for i in range(0, 10):
            entry = mixer.blend(TimelineEntry, teacher=self.teacher, start=x)
            x += timedelta(days=1)
            print(x.__class__)
            entry.save()

        response = self.c.get('/timeline/%s.json?start=2013-01-01&end=2016-01-03' % self.teacher.user.username)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)


class TestFormAPIHelpers(ClientTestCase):
    def setUp(self):
        self.teacher = create_teacher()
        self.lesson = mixer.blend(lessons.MasterClass, host=self.teacher)
        self.entry = TimelineEntry(
            teacher=self.teacher,
            lesson=self.lesson,
            start=datetime(2016, 1, 18, 14, 10),
            end=datetime(2016, 1, 18, 14, 40),
            allow_overlap=False,
        )

        mixer.blend(WorkingHours, teacher=self.teacher, weekday=0, start='13:00', end='15:00')

        self.entry.save()
        super().setUp()

    def test_check_overlap_true(self):
        overlaps = self.__check_entry(
            username=self.teacher.user.username,
            start='2016-01-18 14:30',
            end='2016-01-18 15:00',
        )
        self.assertTrue(overlaps['is_overlapping'])

    def test_check_overlap_false(self):
        not_overlaps = self.__check_entry(
            username=self.teacher.user.username,
            start='2016-01-18 14:45',
            end='2016-01-18 15:15'
        )
        self.assertFalse(not_overlaps['is_overlapping'])

    def test_check_hours_true(self):
        fits = self.__check_entry(
            username=self.teacher.user.username,
            start='2032-05-03 14:00',  # monday
            end='2032-05-03 14:30',
        )
        self.assertTrue(fits['is_fitting_hours'])

    def test_check_hours_false(self):
        fits = self.__check_entry(
            username=self.teacher.user.username,
            start='2032-05-03 14:00',  # monday
            end='2032-05-03 15:30',  # half-hour late
        )
        self.assertFalse(fits['is_fitting_hours'])

    def __check_entry(self, username, start, end):
        response = self.c.get(
            '/timeline/%s/check_entry/%s/%s/' % (username, start, end)
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf-8'))
        return result
