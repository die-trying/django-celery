from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from lessons import models as lessons
from market.exceptions import AutoScheduleExpcetion
from teachers import models
from teachers.models import Teacher, WorkingHours
from timeline.models import Entry as TimelineEntry


class TestTeacherManager(TestCase):
    """
    By default, working hours return hours only in future, so your testing
    dates should be in remote future, see http://www.timeanddate.com/calendar/?year=2032&country=1

    """
    def setUp(self):
        self.teacher = create_teacher()

        mixer.blend(WorkingHours, teacher=self.teacher, weekday=0, start='13:00', end='15:00')  # monday
        mixer.blend(WorkingHours, teacher=self.teacher, weekday=1, start='17:00', end='19:00')  # thursday
        models.PLANNING_DELTA = timedelta(hours=2)

    def test_get_free_slots(self):
        """
        Simple test for fetching free slots
        """
        slots = self.teacher.find_free_slots(date=self.tzdatetime(2032, 5, 3))
        self.assertEquals(len(slots), 4)

        def time(slot):
            return slot.strftime('%H:%M')

        self.assertEqual(time(slots[0]), '13:00')
        self.assertEqual(time(slots[-1]), '14:30')

        slots = self.teacher.find_free_slots(date=self.tzdatetime(2032, 5, 3), period=timedelta(minutes=20))
        self.assertEquals(len(slots), 6)
        self.assertEqual(time(slots[0]), '13:00')
        self.assertEqual(time(slots[1]), '13:20')
        self.assertEqual(time(slots[-1]), '14:40')

        slots = self.teacher.find_free_slots(date=self.tzdatetime(2032, 5, 5))
        self.assertIsNone(slots)  # should not throw DoesNotExist

    def test_get_free_slots_for_dates(self):
        dates = (
            self.tzdatetime(2032, 5, 3),
            self.tzdatetime(2032, 5, 5),
        )

        res = list(self.teacher.free_slots_for_dates(dates))
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]['slots']), 4)

    def test_get_free_slots_from_past(self):
        """
        Make sure, that timeline slots are not returned from distant past
        """
        slots = self.teacher.find_free_slots(self.tzdatetime(2012, 2, 6))  # monday, but 12 years ago
        self.assertEquals(len(slots), 0)  # should not return any

    @freeze_time('2016-07-25 14:30')
    @override_settings(TIME_ZONE='UTC')
    def test_get_free_slots_today(self):
        """
        Set the clock to the middle of teacher working interval — available
        slots count should be reduced.
        """
        slots = self.teacher.find_free_slots(date=self.tzdatetime(2016, 7, 25))
        self.assertEquals(len(slots), 1)  # should return 1 slot instead of 4

    def test_autoschedule_ends_this_day(self):
        afternight_working_hours = MagicMock()
        afternight_working_hours.start = self.tzdatetime(2032, 12, 5, 23, 30)
        afternight_working_hours.end = self.tzdatetime(2032, 12, 6, 4, 30)

        with patch('teachers.models.WorkingHoursManager.for_date', return_value=afternight_working_hours):
            res = self.teacher.find_free_slots(date=self.tzdatetime(2032, 12, 5))
            self.assertEqual(len(res), 1)

    def test_free_slots_for_lesson_type(self):
        """
        Test for getting free time slots for a certain lesson type.
        """
        master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        entry = TimelineEntry(teacher=self.teacher,
                              lesson=master_class,
                              start=self.tzdatetime(2032, 5, 3, 14, 10),
                              end=self.tzdatetime(2032, 5, 3, 14, 40)
                              )
        entry.save()
        lesson_type = ContentType.objects.get_for_model(master_class)

        slots = self.teacher.find_free_slots(date=self.tzdatetime(2032, 5, 3), lesson_type=lesson_type.pk)
        self.assertEquals(len(slots), 1)

        slots = self.teacher.find_free_slots(date=self.tzdatetime(2032, 5, 5), lesson_type=lesson_type.pk)
        self.assertEquals(len(slots), 0)  # there is no master classes, planned on 2032-05-05

    def test_free_slots_for_lesson_type_validates_with_auto_schedule(self):
        master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        entry = TimelineEntry(teacher=self.teacher,
                              lesson=master_class,
                              start=self.tzdatetime(2032, 5, 3, 14, 10),
                              end=self.tzdatetime(2032, 5, 3, 14, 40)
                              )
        entry.save()
        lesson_type = ContentType.objects.get_for_model(master_class)
        with patch('timeline.models.Entry.clean') as clean:
            clean.side_effect = AutoScheduleExpcetion(message='testing')

            slots = self.teacher.find_free_slots(date=self.tzdatetime(2032, 5, 3), lesson_type=lesson_type.pk)
            self.assertEqual(len(slots), 0)

    def test_free_slots_for_lesson(self):
        """
        Test for getting free time slots for a particular teacher with particular
        lesson
        """
        other_teacher = create_teacher()

        master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        other_master_class = mixer.blend(lessons.MasterClass, host=other_teacher)

        entry = TimelineEntry(teacher=self.teacher,
                              lesson=master_class,
                              start=self.tzdatetime(2032, 5, 3, 14, 10),
                              end=self.tzdatetime(2032, 5, 3, 14, 40)
                              )
        entry.save()
        other_entry = TimelineEntry(teacher=other_teacher,
                                    lesson=other_master_class,
                                    start=self.tzdatetime(2032, 5, 3, 14, 10),
                                    end=self.tzdatetime(2032, 5, 3, 14, 40)
                                    )
        other_entry.save()
        slots = self.teacher.find_free_slots(self.tzdatetime(2032, 5, 3), lesson_id=master_class.pk)
        self.assertEquals(len(slots), 1)
        slots = self.teacher.find_free_slots(self.tzdatetime(2032, 5, 3), lesson_id=other_master_class.pk)
        self.assertEquals(len(slots), 0)

    def find_lessons(self):
        found = Teacher.find_lessons(date=self.tzdatetime(2032, 5, 3), lesson_type=lessons.MasterClass.get_contenttype().pk)
        self.assertIsNone(found)

    def test_two_teachers_for_single_slot(self):
        """
        Check if find_free_slots returns only slots of selected teacher
        """
        other_teacher = create_teacher()
        master_class = mixer.blend(lessons.MasterClass, host=other_teacher)
        entry = TimelineEntry(teacher=other_teacher,
                              lesson=master_class,
                              start=self.tzdatetime(2032, 5, 3, 14, 10),
                              end=self.tzdatetime(2032, 5, 3, 14, 40)
                              )
        entry.save()
        lesson_type = ContentType.objects.get_for_model(master_class)

        slots = self.teacher.find_free_slots(date=self.tzdatetime(2032, 5, 3), lesson_type=lesson_type.pk)
        self.assertEquals(len(slots), 0)  # should not return anything — we are checking slots for self.teacher, not other_teacher

    def test_find_teacher_by_date(self):
        """
        Find a teacher that can work for distinct date without a specific event
        """
        free_teachers = Teacher.objects.find_free(date=self.tzdatetime(2032, 5, 3))
        self.assertEquals(free_teachers[0], self.teacher)

        free_teachers = Teacher.objects.find_free(date=self.tzdatetime(2017, 7, 20))
        self.assertEquals(len(free_teachers), 0)  # no one works on wednesdays

    def test_get_teachers_by_lesson_type(self):
        """
        Add two timeline entries for two teachers and find their slots by
        lesson_type
        """
        second_teacher = create_teacher()
        first_master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        second_master_class = mixer.blend(lessons.MasterClass, host=second_teacher)

        first_entry = TimelineEntry(teacher=self.teacher,
                                    lesson=first_master_class,
                                    start=self.tzdatetime(2032, 5, 3, 14, 10),
                                    end=self.tzdatetime(2032, 5, 3, 14, 40)
                                    )
        first_entry.save()

        second_entry = TimelineEntry(teacher=second_teacher,
                                     lesson=second_master_class,
                                     start=self.tzdatetime(2032, 5, 3, 14, 10),
                                     end=self.tzdatetime(2032, 5, 3, 14, 40)
                                     )
        second_entry.save()
        lesson_type = ContentType.objects.get_for_model(first_master_class)
        free_teachers = Teacher.objects.find_free(date=self.tzdatetime(2032, 5, 3), lesson_type=lesson_type.pk)
        self.assertEquals(len(free_teachers), 2)

        free_teachers = Teacher.objects.find_free(date=self.tzdatetime(2032, 5, 5), lesson_type=lesson_type.pk)
        self.assertEquals(len(free_teachers), 0)  # there is no master classes. planned on 2032-05-05

    def test_get_teachers_by_lesson(self):
        """
        Find teachers for a particular lesson
        """
        first_master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        first_entry = TimelineEntry(teacher=self.teacher,
                                    lesson=first_master_class,
                                    start=self.tzdatetime(2032, 5, 3, 14, 10),
                                    end=self.tzdatetime(2032, 5, 3, 14, 40)
                                    )
        first_entry.save()
        free_teachers = Teacher.objects.find_free(date=self.tzdatetime(2032, 5, 3), lesson_id=first_master_class.pk)
        self.assertEquals(len(free_teachers), 1)

    def test_get_teachers_by_lesson_that_does_not_require_a_timeline_entry(self):
        ordinary_lesson_type = lessons.OrdinaryLesson.get_contenttype()
        teachers = Teacher.objects.find_free(date=self.tzdatetime(2032, 5, 3), lesson_type=ordinary_lesson_type.pk)
        self.assertEquals(len(teachers), 1)
        print(teachers[0].free_slots)
        self.assertEquals(len(teachers[0].free_slots), 4)  # should find all timeline entries because ordinary lesson does not require a timeline entry

    def test_find_lessons_return_nothing(self):
        res = Teacher.objects.find_lessons(date=self.tzdatetime(2032, 5, 3))
        self.assertEqual(len(res), 0)  # should not throw anything

    @freeze_time('2032-05-02')
    def test_find_lessons_return_a_lesson(self):
        master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        mixer.blend(
            TimelineEntry,
            teacher=self.teacher,
            lesson=master_class,
            start=self.tzdatetime(2032, 5, 3, 15, 30),
        )
        res = Teacher.objects.find_lessons(date=self.tzdatetime(2032, 5, 3))
        self.assertEqual(len(res), 1)

    @freeze_time('2032-05-03 15:31')
    @override_settings(TIME_ZONE='UTC')
    def test_find_lessons_ignore_passed_lessons(self):
        master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        mixer.blend(
            TimelineEntry,
            teacher=self.teacher,
            lesson=master_class,
            start=self.tzdatetime(2032, 5, 3, 15, 30),
        )
        res = Teacher.objects.find_lessons(date=self.tzdatetime(2032, 5, 3))
        self.assertEqual(len(res), 0)

    @freeze_time('2032-05-02')
    def test_find_lessons_traverses_filter_args(self):
        master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        paired_lesson = mixer.blend(lessons.PairedLesson, host=self.teacher)
        mixer.blend(
            TimelineEntry,
            teacher=self.teacher,
            lesson=master_class,
            start=self.tzdatetime(2032, 5, 3, 15, 30),
        )
        mixer.blend(
            TimelineEntry,
            teacher=self.teacher,
            lesson=paired_lesson,
            start=self.tzdatetime(2032, 5, 3, 16, 30),
        )

        res = Teacher.objects.find_lessons(date=self.tzdatetime(2032, 5, 3))
        self.assertEqual(len(res), 2)

        res = Teacher.objects.find_lessons(date=self.tzdatetime(2032, 5, 3), lesson_type=master_class.get_contenttype())
        self.assertEqual(len(res), 1)

    @freeze_time('2032-05-02')
    def test_find_lessons_ignores_non_free_entries(self):
        master_class = mixer.blend(lessons.MasterClass, host=self.teacher)
        mixer.blend(
            TimelineEntry,
            teacher=self.teacher,
            lesson=master_class,
            start=self.tzdatetime(2032, 5, 3, 15, 30),
            slots=5,
            taken_slots=5,
        )
        res = Teacher.objects.find_lessons(date=self.tzdatetime(2032, 5, 3))
        self.assertEqual(len(res), 0)

    def test_can_finish_classes(self):
        res = Teacher.objects.can_finish_classes()
        self.assertEqual(res[1][0], self.teacher.pk)
        self.assertIn(self.teacher.user.crm.full_name, res[1][1])
