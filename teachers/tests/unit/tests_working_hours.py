from unittest.mock import patch

from django.test import override_settings
from django.utils import timezone
from django.utils.dateparse import parse_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from teachers.models import WorkingHours


class TestWorkingHours(TestCase):
    def setUp(self):
        self.teacher = create_teacher()
        self.monday = mixer.blend(WorkingHours, teacher=self.teacher, weekday=0, start='13:00', end='15:00')  # monday
        self.tuesday = mixer.blend(WorkingHours, teacher=self.teacher, weekday=1, start='17:00', end='19:00')  # tuesday

    def test_working_hours_for_date(self):
        """
        Get datetime.datetime objects for start and end working hours
        """
        working_hours_monday = self.teacher.working_hours.for_date(date=self.tzdatetime(2032, 5, 3))
        self.assertIsNotNone(working_hours_monday)
        self.assertEqual(working_hours_monday.start.strftime('%Y-%m-%d %H:%M'), '2032-05-03 13:00')
        self.assertEqual(working_hours_monday.end.strftime('%Y-%m-%d %H:%M'), '2032-05-03 15:00')

        working_hours_wed = self.teacher.working_hours.for_date(date=self.tzdatetime(2016, 5, 5))
        self.assertIsNone(working_hours_wed)  # should not throw DoesNotExist

    @override_settings(TIME_ZONE='US/Eastern')
    def test_working_hours_for_date_is_timezone_aware(self):
        """
        Check if WorkingHours.for_date localizes timezone to the user's one
        """
        timezone.activate('Europe/Moscow')
        tuesday = self.tzdatetime('Europe/Moscow', 2032, 5, 3, 2, 0)

        with patch('teachers.models.WorkingHoursManager.get') as get:
            try:
                self.teacher.working_hours.for_date(date=tuesday)
            except:
                pass

            get.assert_called_once_with(weekday=0)

    def test_working_hours_fits_ok(self):
        self.assertTrue(self._does_fit('13:00'))
        self.assertTrue(self._does_fit('13:30'))
        self.assertTrue(self._does_fit('14:30'))
        self.assertTrue(self._does_fit('14:59'))

    def test_working_hours_fits_fail(self):
        self.assertFalse(self._does_fit('11:30'))
        self.assertFalse(self._does_fit('12:30'))
        self.assertFalse(self._does_fit('15:01'))
        self.assertFalse(self._does_fit('15:30'))

    def _does_fit(self, t):
        return self.monday.does_fit(
            parse_time(t)
        )
