import json
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from mixer.backend.django import mixer

from elk.utils.testing import ClientTestCase, create_teacher
from lessons import models as lessons
from timeline.models import Entry as TimelineEntry

from freezegun import freeze_time


@freeze_time('2016-06-29 12:00')
class EntryCRUDTest(ClientTestCase):
    """
    Test hand-crafted form for event editing throught the calendar.
    """
    def setUp(self):
        self.teacher = create_teacher()
        self.lesson = mixer.blend(lessons.MasterClass, host=self.teacher, duration=timedelta(minutes=33))
        self.lesson_type = ContentType.objects.get_for_model(lessons.MasterClass).pk

    def testCRUD(self):
        self._create()
        self._update()
        self._delete()

    def test_cancel_link_presence(self):
        """
        Delete link should be present by default and should be hidden for past entries
        """
        self._create()
        entry = TimelineEntry.objects.get(pk=self.added_entry['id'])

        response = self.c.get('/timeline/%s/%d/update/' % (self.teacher.user.username, entry.pk))
        self.assertNotContains(response, 'p class="timeline-entry-form__delete"')

        entry.start = self.tzdatetime(2016, 6, 28, 12, 0)  # a day before
        entry.save()

        response = self.c.get('/timeline/%s/%d/update/' % (self.teacher.user.username, entry.pk))
        self.assertNotContains(response, 'p class="timeline-entry-form__delete"')

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

        end = parse_datetime(self.added_entry['end'])
        reference = timezone.make_aware(parse_datetime('2016-06-29 15:33:00'))
        self.assertEqual(end, reference)
        self.assertIn(self.lesson.name, self.added_entry['title'])

        entry = TimelineEntry.objects.get(pk=self.added_entry['id'])
        self.assertIsNotNone(entry)

        self.assertTrue(entry.allow_besides_working_hours)

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

        end = parse_datetime(self.added_entry['end'])
        reference = timezone.make_aware(parse_datetime('2016-06-29 16:33:00'))
        self.assertEqual(end, reference)
        self.assertIn(self.lesson.name, self.added_entry['title'])

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
