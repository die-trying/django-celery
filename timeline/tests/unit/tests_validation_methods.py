import json
from datetime import datetime

from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import ClientTestCase, create_teacher
from teachers.models import WorkingHours
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
