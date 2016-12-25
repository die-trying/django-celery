from datetime import timedelta

from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from lessons import models as lessons
from timeline.models import Entry as TimelineEntry


@freeze_time('2032-12-01 12:05')
class TestLessonsStartingSoon(TestCase):
    def setUp(self):
        self.host = create_teacher(works_24x7=True)

        self.lesson = mixer.blend(lessons.MasterClass, host=self.host, photo=mixer.RANDOM)

        self.entry = mixer.blend(
            TimelineEntry,
            teacher=self.host,
            lesson=self.lesson,
            start=self.tzdatetime(2032, 12, 5, 13, 00)
        )

    def test_starting_soon_for_lesson_type_none(self):
        starting_soon = TimelineEntry.objects.hosted_lessons_starting_soon(lesson_types=[lessons.PairedLesson.get_contenttype()])
        starting_soon = list(starting_soon)
        self.assertEqual(len(starting_soon), 0)

    def test_starting_soon_for_lesson_type_1(self):
        starting_soon = TimelineEntry.objects.hosted_lessons_starting_soon(lesson_types=[lessons.MasterClass.get_contenttype()])
        starting_soon = list(starting_soon)
        self.assertEqual(len(starting_soon), 1)

    def test_starting_soon_returns_lesosns(self):
        starting_soon = TimelineEntry.objects.hosted_lessons_starting_soon(lesson_types=[lessons.MasterClass.get_contenttype()])

        starting_soon = list(starting_soon)

        self.assertIsInstance(starting_soon[0], lessons.MasterClass)

    def test_starting_soon_returns_only_lessons_with_photos(self):
        self.lesson.photo = None
        self.lesson.save()

        starting_soon = TimelineEntry.objects.hosted_lessons_starting_soon(lesson_types=[lessons.PairedLesson.get_contenttype()])
        starting_soon = list(starting_soon)
        self.assertEqual(len(starting_soon), 0)

    @freeze_time('2032-12-10 12:00')
    def test_starting_soon_works_only_with_future_lessons(self):
        """
        Move 5 days forward and check that lesson should disappear
        """
        starting_soon = TimelineEntry.objects.hosted_lessons_starting_soon(lesson_types=[lessons.MasterClass.get_contenttype()])
        starting_soon = list(starting_soon)
        self.assertEqual(len(starting_soon), 0)

    def test_starting_soon_returns_only_free_entries(self):
        """
        Reduce the number of available students slots to 0 and check
        if hosted_lessons_starting_soon() does not return a lesson with that timeline
        entry.
        """
        self.lesson.slots = 0
        self.lesson.save()

        self.entry.slots = 0
        self.entry.save()

        starting_soon = TimelineEntry.objects.hosted_lessons_starting_soon(lesson_types=[lessons.MasterClass.get_contenttype()])
        starting_soon = list(starting_soon)
        self.assertEqual(len(starting_soon), 0)

    def test_starting_soon_returns_only_one_distinct_lesson(self):
        """
        Create 5 timeline entries and check if hosted_lessons_starting_soon() returns
        only one of them.
        """
        for i in range(0, 5):
            self.entry = mixer.blend(
                TimelineEntry,
                teacher=self.host,
                lesson=self.lesson,
                start=self.tzdatetime(2032, 12, 1, 13, 00) + timedelta(hours=i)
            )

        starting_soon = TimelineEntry.objects.hosted_lessons_starting_soon(lesson_types=[lessons.MasterClass.get_contenttype()])
        starting_soon = list(starting_soon)
        self.assertEqual(len(starting_soon), 1)  # should be only 1 lesson, because all lessons are equal

    def test_starting_soon_does_not_fail_on_usual_lessons(self):
        starting_soon = TimelineEntry.objects.hosted_lessons_starting_soon(lesson_types=[lessons.OrdinaryLesson.get_contenttype()])
        starting_soon = list(starting_soon)
        self.assertEqual(len(starting_soon), 0)  # should not throw anything, silently return []

    def test_starting_soon_planning_delta_traversal(self):
        starting_soon = TimelineEntry.objects.hosted_lessons_starting_soon(lesson_types=[lessons.MasterClass.get_contenttype()], delta=timedelta(days=100))

        starting_soon = list(starting_soon)
        self.assertEqual(len(starting_soon), 0)  # should not find anything because the only lesson available will happen 5 days ahead, but the planning delta is 100 days


@freeze_time('2032-12-01 12:05')
class TestFindTimelineEntryByStart(TestCase):
    def setUp(self):
        self.host = create_teacher(works_24x7=True)

        self.lesson = mixer.blend(lessons.MasterClass, host=self.host, photo=mixer.RANDOM)

        self.entry = mixer.blend(
            TimelineEntry,
            teacher=self.host,
            lesson=self.lesson,
            start=self.tzdatetime(2032, 12, 5, 13, 00)
        )

    def test_find_ok(self):
        entry = TimelineEntry.objects.by_start(teacher=self.host, start=self.entry.start, lesson=self.lesson)

        self.assertEqual(entry, self.entry)

    def test_find_none(self):
        another_guy = create_teacher()
        entry = TimelineEntry.objects.by_start(teacher=another_guy, start=self.entry.start, lesson=self.lesson)

        self.assertIsNone(entry)  # should not throw anything

    def test_finds_only_lessons_available_for_scheduling(self):
        """
        Reduce the number of available students slots to 0 and check
        if by_start() does not return a lesson with that timeline
        entry.
        """
        self.lesson.slots = 0
        self.lesson.save()

        self.entry.slots = 0
        self.entry.save()

        entry = TimelineEntry.objects.by_start(teacher=self.host, start=self.entry.start, lesson=self.lesson)

        self.assertIsNone(entry)
