import json
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import ClientTestCase, create_teacher
from teachers.models import WorkingHours
from timeline.models import Entry as TimelineEntry


class SlotAvailableTest(TestCase):
    def setUp(self):
        self.teacher = create_teacher()
        self.lesson = mixer.blend(lessons.OrdinaryLesson, teacher=self.teacher)

        self.big_entry = mixer.blend(TimelineEntry,
                                     teacher=self.teacher,
                                     start=parse_datetime('2016-01-02 18:00'),
                                     end=parse_datetime('2016-01-03 12:00'),
                                     )

    def test_overlap(self):
        """
        Create two entries — one overlapping with the big_entry, and one — not
        """
        overlapping_entry = TimelineEntry(teacher=self.teacher,
                                          start=parse_datetime('2016-01-03 04:00'),
                                          end=parse_datetime('2016-01-03 04:30'),
                                          )
        self.assertTrue(overlapping_entry.is_overlapping())

        non_overlapping_entry = TimelineEntry(teacher=self.teacher,
                                              start=parse_datetime('2016-01-03 12:00'),
                                              end=parse_datetime('2016-01-03 12:30'),
                                              )
        self.assertFalse(non_overlapping_entry.is_overlapping())

    def test_overlapping_with_different_teacher(self):
        """
        Check, if it's pohuy, that an entry overlapes entry of the other teacher
        """
        other_teacher = create_teacher()
        test_entry = TimelineEntry(teacher=other_teacher,
                                   start=parse_datetime('2016-01-03 04:00'),
                                   end=parse_datetime('2016-01-03 04:30'),
                                   )
        self.assertFalse(test_entry.is_overlapping())

    def test_two_equal_entries(self):
        """
        Two equal entries should overlap each other
        """
        first_entry = mixer.blend(TimelineEntry,
                                  teacher=self.teacher,
                                  start=parse_datetime('2016-01-03 04:00'),
                                  end=parse_datetime('2016-01-03 04:30'),
                                  )
        first_entry.save()

        second_entry = TimelineEntry(teacher=self.teacher,
                                     start=parse_datetime('2016-01-03 04:00'),
                                     end=parse_datetime('2016-01-03 04:30'),
                                     )
        self.assertTrue(second_entry.is_overlapping())

    def test_cant_save_due_to_overlap(self):
        """
        We should not have posibillity to save a timeline entry, that can not
        be created
        """
        overlapping_entry = TimelineEntry(teacher=self.teacher,
                                          lesson=self.lesson,
                                          start=parse_datetime('2016-01-03 04:00'),
                                          end=parse_datetime('2016-01-03 04:30'),
                                          allow_overlap=False,  # excplicitly say, that entry can't overlap other ones
                                          )
        with self.assertRaises(ValidationError):
            overlapping_entry.save()

    def test_save_again_entry_that_does_not_allow_overlapping(self):
        """
        Create an entry that does not allow overlapping and the save it again
        """
        entry = TimelineEntry(
            teacher=self.teacher,
            lesson=self.lesson,
            start=parse_datetime('2016-01-10 04:00'),
            end=parse_datetime('2016-01-10 04:30'),
            allow_overlap=False
        )
        entry.save()

        entry.start = parse_datetime('2016-01-10 04:01')  # change random parameter
        entry.save()

        self.assertIsNotNone(entry)  # should not throw anything

    def test_working_hours(self):
        mixer.blend(WorkingHours, teacher=self.teacher, start='12:00', end='13:00', weekday=0)
        entry_besides_hours = TimelineEntry(teacher=self.teacher,
                                            start=parse_datetime('2032-05-03 04:00'),
                                            end=parse_datetime('2032-05-03 04:30'),
                                            )
        self.assertFalse(entry_besides_hours.is_fitting_working_hours())

        entry_within_hours = TimelineEntry(teacher=self.teacher,
                                           start=parse_datetime('2032-05-03 12:30'),
                                           end=parse_datetime('2032-05-03 13:00'),
                                           )
        self.assertTrue(entry_within_hours.is_fitting_working_hours())

    def test_working_hours_multidate(self):
        """
        Test checking working hours when lesson starts in one day, and ends on
        another. This will be frequent situations, because our teachers are
        in different timezones.
        """
        mixer.blend(WorkingHours, teacher=self.teacher, start='23:00', end='23:59', weekday=0)
        mixer.blend(WorkingHours, teacher=self.teacher, start='00:00', end='02:00', weekday=1)

        entry_besides_hours = TimelineEntry(teacher=self.teacher,
                                            start=parse_datetime('2032-05-03 22:00'),  # does not fit
                                            end=parse_datetime('2016-07-26 00:30'),
                                            )
        self.assertFalse(entry_besides_hours.is_fitting_working_hours())

        entry_besides_hours.start = parse_datetime('2032-05-03 23:30')  # fits
        entry_besides_hours.end = parse_datetime('2016-07-26 02:30')    # does not fit
        self.assertFalse(entry_besides_hours.is_fitting_working_hours())

        entry_within_hours = TimelineEntry(teacher=self.teacher,
                                           start=parse_datetime('2032-05-03 23:30'),
                                           end=parse_datetime('2016-07-26 00:30'),
                                           )
        self.assertTrue(entry_within_hours.is_fitting_working_hours())

        # flex scope
        #
        # entry_within_hours.end = parse_datetime('2032-05-03 00:00')
        # self.assertTrue(entry_within_hours.is_fitting_working_hours())

    def test_working_hours_nonexistant(self):
        entry = TimelineEntry(teacher=self.teacher,
                              start=parse_datetime('2032-05-03 22:00'),  # does not fit
                              end=parse_datetime('2016-07-26 00:30'),
                              )
        self.assertFalse(entry.is_fitting_working_hours())  # should not throw anything

    def test_cant_save_due_to_not_fitting_working_hours(self):
        """
        Create an entry that does not fit into teachers working hours
        """
        entry = TimelineEntry(
            teacher=self.teacher,
            lesson=self.lesson,
            start=parse_datetime('2032-05-03 13:30'),  # monday
            end=parse_datetime('2032-05-03 14:00'),
            allow_besides_working_hours=False
        )
        with self.assertRaises(ValidationError):
            entry.save()
        mixer.blend(WorkingHours, teacher=self.teacher, weekday=0, start='13:00', end='15:00')  # monday
        entry.save()
        self.assertIsNotNone(entry.pk)  # should be saved now


class EntryCRUDTest(ClientTestCase):
    """
    Test hand-crafted form for event editing throught the calendar.
    """
    def setUp(self):
        self.teacher = create_teacher()
        self.lesson = mixer.blend(lessons.MasterClass, host=self.teacher, duration=timedelta(minutes=33))
        self.lesson_type = ContentType.objects.get_for_model(lessons.MasterClass).pk

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

        end = parse_datetime(self.added_entry['end'])
        reference = timezone.make_aware(parse_datetime('2016-06-29 15:33:00'))
        self.assertEqual(end, reference)
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

        end = parse_datetime(self.added_entry['end'])
        reference = timezone.make_aware(parse_datetime('2016-06-29 16:33:00'))
        self.assertEqual(end, reference)
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

        now = timezone.now()
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

            start = parse_datetime(i['start'])
            end = parse_datetime(i['end'])
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
