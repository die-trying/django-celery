from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from lessons import models as lessons
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
