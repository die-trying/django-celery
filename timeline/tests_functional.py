import json
from datetime import datetime, timedelta

import iso8601
from django.contrib.contenttypes.models import ContentType
from django.utils.dateformat import format
from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import ClientTestCase, create_teacher
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

        self.added_entry = self.__get_entry_from_json()

        self.assertEqual(self.added_entry['end'], '2016-06-29T15:33:00')
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

        self.added_entry = self.__get_entry_from_json()

        self.assertEqual(self.added_entry['end'], '2016-06-29T16:33:00')
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

    def __get_entry_from_json(self):
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

    def create_user_json(self):
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

            self.assertEqual(i['start'],
                             format(mocked_entry.start, 'c')
                             )
            self.assertEqual(i['end'],
                             format(now + duration, 'c')
                             )

    def create_user_json_filter(self):
        x = iso8601.parse_date('2016-01-01')
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

        super().setUp()

    def test_check_overlap(self):
        entry = TimelineEntry(
            teacher=self.teacher,
            lesson=self.lesson,
            start=datetime(2016, 1, 18, 14, 10),
            end=datetime(2016, 1, 18, 14, 40),
            allow_overlap=False,
        )
        entry.save()

        overlaps = self.__get_overlap_response(
            username=self.teacher.user.username,
            start='2016-01-18 14:30',
            end='2016-01-18 15:00',
        )
        self.assertTrue(overlaps)

        not_overlaps = self.__get_overlap_response(
            username=self.teacher.user.username,
            start='2016-01-18 14:45',
            end='2016-01-18 15:15'
        )
        self.assertFalse(not_overlaps)

        not_overlaps = self.__get_overlap_response(
            username=self.teacher.user.username,
            start='2016-01-18 14:30',
            end='2016-01-18 15:00',
            query_string_append='&entry=%d' % entry.pk,
        )
        self.assertFalse(not_overlaps)

    def __get_overlap_response(self, username, start, end, query_string_append=''):
        response = self.c.get(
            '/timeline/%s/check_overlap/?start=%s&end=%s%s' % (username, start, end, query_string_append)
        )
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content.decode('utf-8'))
