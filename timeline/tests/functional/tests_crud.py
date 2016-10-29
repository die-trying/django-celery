import json
from datetime import timedelta

from django.test import override_settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import ClientTestCase, create_teacher
from lessons import models as lessons
from timeline.models import Entry as TimelineEntry


@freeze_time('2016-06-29 12:00')
@override_settings(TIME_ZONE='Europe/Moscow')
class EntryCRUDTest(ClientTestCase):
    """
    Test hand-crafted form for event editing throught the calendar.
    """
    def setUp(self):
        self.teacher = create_teacher(works_24x7=True)
        self.lesson = mixer.blend(lessons.MasterClass, host=self.teacher, duration=timedelta(minutes=33))
        self.lesson_type = self.lesson.get_contenttype().pk

    def testCRUD(self):
        self._create()
        self._update()
        self._delete()

    def test_login_required(self):
        self.c.logout()
        entry = mixer.blend(TimelineEntry, teacher=self.teacher)
        delete_link = '/timeline/%s/%d/delete/' % (self.teacher.user.username, entry.pk)

        response = self.c.get(delete_link)

        self.assertRedirects(response, '/admin/login/?next=%s' % delete_link)

        entry.refresh_from_db()  # assure entry in constant
        self.assertIsNotNone(entry.pk)

    def _create(self):
        response = self.c.post('/timeline/%s/add/' % self.teacher.user.username, {
            'lesson_type': self.lesson_type,
            'lesson_id': self.lesson.pk,
            'teacher': self.teacher.pk,
            'start_0': '06/29/2016',
            'start_1': '15:00',
            'duration': '00:33',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.teacher.timeline_entries.count(), 1)

        self.added_entry = self.__get_entry_from()

        end = timezone.localtime(parse_datetime(self.added_entry['end']))
        self.assertEqual(end, self.tzdatetime(2016, 6, 29, 15, 33))

        self.assertIsNotNone(TimelineEntry.objects.get(pk=self.added_entry['id']))

    def _update(self):
        pk = self.added_entry['id']

        response = self.c.post('/timeline/%s/%d/' % (self.teacher.user.username, pk), {
            'lesson_type': self.lesson_type,
            'lesson_id': self.lesson.pk,
            'teacher': self.teacher.pk,
            'start_0': '06/29/2016',
            'start_1': '16:00',  # moved fwd for 1 hour
            'duration': '00:33',
        })
        self.assertEqual(response.status_code, 302)

        self.added_entry = self.__get_entry_from()

        end = parse_datetime(self.added_entry['end'])
        self.assertEqual(end, self.tzdatetime(2016, 6, 29, 16, 33))

    def _delete(self):
        pk = self.added_entry['id']
        response = self.c.get('/timeline/%s/%d/delete/' % (self.teacher.user.username, pk))
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(TimelineEntry.DoesNotExist):  # should be deleted now
            TimelineEntry.objects.get(pk=pk)

    def __get_entry_from(self):
        response = self.c.get('/api/timeline/?teacher=%d&start_0=2016-06-28&start_1=2016-06-30' % self.teacher.pk)
        self.assertEqual(response.status_code, 200)
        entries = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(entries), 1)

        return entries[0]
