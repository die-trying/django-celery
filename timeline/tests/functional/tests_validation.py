import json

from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import ClientTestCase, create_teacher
from teachers.models import Absence, WorkingHours
from timeline.models import Entry as TimelineEntry


class TestCheckEntry(ClientTestCase):
    """
    :view:`timeline.check_entry` is a helper for the timeline creating form
    which checks entry validity — working hours and overlaping
    """
    def setUp(self):
        self.teacher = create_teacher()
        self.lesson = mixer.blend(lessons.MasterClass, host=self.teacher)
        self.entry = TimelineEntry(
            teacher=self.teacher,
            lesson=self.lesson,
            start=self.tzdatetime('Europe/Moscow', 2016, 1, 18, 14, 10),
            end=self.tzdatetime('Europe/Moscow', 2016, 1, 18, 14, 40),
            allow_overlap=False,
        )

        self.entry.save()

        mixer.blend(WorkingHours, teacher=self.teacher, weekday=0, start='13:00', end='15:00')

        self.absence = Absence(
            type='vacation',
            teacher=self.teacher,
            start=self.tzdatetime(2032, 5, 3, 0, 0),
            end=self.tzdatetime(2032, 5, 3, 23, 59),
        )
        self.absence.save()

    def test_check_overlap_true(self):
        res = self.__check_entry(
            start='2016-01-18 14:30',
            end='2016-01-18 15:00',
        )
        self.assertTrue(res['is_overlapping'])

    def test_check_overlap_false(self):
        res = self.__check_entry(
            start='2016-01-18 14:45',
            end='2016-01-18 15:15'
        )
        self.assertFalse(res['is_overlapping'])

    def test_check_hours_true(self):
        res = self.__check_entry(
            start='2032-05-03 14:00',  # monday
            end='2032-05-03 14:30',
        )
        self.assertTrue(res['is_fitting_hours'])

    def test_check_hours_false(self):
        res = self.__check_entry(
            start='2032-05-03 14:00',  # monday
            end='2032-05-03 15:30',  # half-hour late
        )
        self.assertFalse(res['is_fitting_hours'])

    def test_teacher_is_present_true(self):
        res = self.__check_entry(
            start='2032-05-01 14:00',
            end='2032-05-01 14:30',
        )
        self.assertTrue(res['teacher_is_present'])

    def test_teacher_is_present_false(self):
        res = self.__check_entry(
            start='2032-05-03 14:00',  # this day teacher is on vacation
            end='2032-05-03 14:30',
        )
        self.assertFalse(res['teacher_is_present'])

    def __check_entry(self, start, end):
        response = self.c.get(
            '/timeline/%s/check_entry/%s/%s/' % (self.teacher.user.username, start, end)
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf-8'))
        return result
