from django.test import override_settings
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from extevents.models import ExternalEvent
from lessons import models as lessons
from market.exceptions import AutoScheduleExpcetion
from teachers.models import Absence, WorkingHours
from timeline.exceptions import DoesNotFitWorkingHours
from timeline.models import Entry as TimelineEntry


@override_settings(TIME_ZONE='UTC')
@freeze_time('2005-02-12 12:22')
class TestOverlapValidation(TestCase):
    fixtures = ['lessons']

    def setUp(self):
        self.teacher = create_teacher()
        self.lesson = lessons.OrdinaryLesson.get_default()

        self.big_entry = mixer.blend(
            TimelineEntry,
            teacher=self.teacher,
            start=self.tzdatetime(2016, 1, 2, 18, 0),
            end=self.tzdatetime(2016, 1, 3, 12, 0),
        )

    def test_cant_save_due_to_overlap(self):
        overlapping_entry = TimelineEntry(
            teacher=self.teacher,
            lesson=self.lesson,
            start=self.tzdatetime(2016, 1, 3, 4, 0),
            end=self.tzdatetime(2016, 1, 3, 4, 30),
        )
        with self.assertRaises(AutoScheduleExpcetion):  # should conflict with self.big_entry
            overlapping_entry.clean()

    def test_no_validation_when_more_then_one_student_has_signed(self):
        """
        There is no need to validate a timeline entry when it has students
        """
        overlapping_entry = TimelineEntry(
            teacher=self.teacher,
            lesson=self.lesson,
            start=self.tzdatetime(2016, 1, 3, 4, 0),
            end=self.tzdatetime(2016, 1, 3, 4, 30),
            taken_slots=1,
        )
        overlapping_entry.clean()  # should not throw anything
        self.assertTrue(True)

    def test_working_hours(self):
        mixer.blend(WorkingHours, teacher=self.teacher, start='12:00', end='13:00', weekday=0)
        entry_besides_hours = TimelineEntry(
            teacher=self.teacher,
            start=self.tzdatetime(2032, 5, 3, 4, 0),
            end=self.tzdatetime(2032, 5, 3, 4, 30),
        )
        self.assertFalse(entry_besides_hours.is_fitting_working_hours())

        entry_within_hours = TimelineEntry(
            teacher=self.teacher,
            start=self.tzdatetime(2032, 5, 3, 12, 30),
            end=self.tzdatetime(2032, 5, 3, 13, 0),
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

        entry_besides_hours = TimelineEntry(
            teacher=self.teacher,
            start=self.tzdatetime(2032, 5, 3, 22, 0),  # does not fit
            end=self.tzdatetime(2032, 5, 4, 0, 30)
        )
        self.assertFalse(entry_besides_hours.is_fitting_working_hours())

        entry_besides_hours.start = self.tzdatetime(2032, 5, 3, 22, 30)  # does fit
        entry_besides_hours.end = self.tzdatetime(2016, 7, 26, 2, 30)    # does not fit

        self.assertFalse(entry_besides_hours.is_fitting_working_hours())

        entry_within_hours = TimelineEntry(
            teacher=self.teacher,
            start=self.tzdatetime(2032, 5, 3, 23, 30),
            end=self.tzdatetime(2032, 5, 4, 0, 30)
        )
        self.assertTrue(entry_within_hours.is_fitting_working_hours())

    def test_working_hours_nonexistant(self):
        entry = TimelineEntry(
            teacher=self.teacher,
            start=self.tzdatetime(2032, 5, 3, 22, 0),  # does not fit
            end=self.tzdatetime(2032, 5, 3, 22, 30),
        )
        self.assertFalse(entry.is_fitting_working_hours())  # should not throw anything

    def test_cant_save_due_to_not_fitting_working_hours(self):
        """
        Create an entry that does not fit into teachers working hours
        """
        entry = TimelineEntry(
            teacher=self.teacher,
            lesson=self.lesson,
            start=self.tzdatetime(2032, 5, 3, 13, 30),  # monday
            end=self.tzdatetime(2032, 5, 3, 14, 0),
            allow_besides_working_hours=False
        )
        with self.assertRaises(DoesNotFitWorkingHours, msg='Entry does not fit teachers working hours'):
            entry.clean()

    def test_cant_save_due_to_teacher_absence(self):
        entry = TimelineEntry(
            teacher=self.teacher,
            lesson=self.lesson,
            start=self.tzdatetime(2016, 5, 3, 13, 30),
            end=self.tzdatetime(2016, 5, 3, 14, 00),
        )
        vacation = Absence(
            type='vacation',
            teacher=self.teacher,
            start=self.tzdatetime(2016, 5, 2, 00, 00),
            end=self.tzdatetime(2016, 5, 5, 23, 59),
        )
        vacation.save()
        with self.assertRaises(AutoScheduleExpcetion):
            entry.clean()

    def test_cant_save_due_to_teacher_has_events(self):
        entry = TimelineEntry(
            teacher=self.teacher,
            lesson=self.lesson,
            start=self.tzdatetime(2016, 5, 3, 13, 30),
            end=self.tzdatetime(2016, 5, 3, 14, 00),
        )
        mixer.blend(
            ExternalEvent,
            teacher=self.teacher,
            start=self.tzdatetime(2016, 5, 2, 00, 00),
            end=self.tzdatetime(2016, 5, 5, 23, 59),
        )
        with self.assertRaises(AutoScheduleExpcetion):
            entry.clean()
