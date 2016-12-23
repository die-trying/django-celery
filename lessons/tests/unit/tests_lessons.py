from django.core.exceptions import ValidationError
from freezegun import freeze_time
from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import TestCase, create_teacher


@freeze_time('2032-12-01 15:45')
class TestLessonsUnit(TestCase):
    def test_planning_unaccaptable_lesson(self):
        lazy_teacher = create_teacher(accepts_all_lessons=False)  # teacher2 does not accept any lesson, so cannot be planned
        hard_working_teacher = create_teacher()

        with self.assertRaises(ValidationError):
            mixer.blend(lessons.MasterClass, host=lazy_teacher)

        self.assertIsNotNone(mixer.blend(lessons.MasterClass, host=hard_working_teacher))

    def test_type_verbose_name(self):
        l = mixer.blend(lessons.OrdinaryLesson)
        self.assertIn('single', str(l.type_verbose_name))

    def test_long_name(self):
        l = mixer.blend(lessons.OrdinaryLesson)
        self.assertIn('Curated', l.long_name())

    def test_long_name_from_verbose_name(self):
        """
        Trial lessons don't defined custom long name but still have one from verbose_name
        """
        l = mixer.blend(lessons.TrialLesson)
        self.assertIn('First', l.long_name())

    def test_long_name_plural(self):
        l = mixer.blend(lessons.OrdinaryLesson)
        self.assertIn('Curated lessons', l.long_name_plural())

    def test_long_name_plural_from_verbose_name(self):
        """
        Trial lessons don't defined custom long name but still have one from verbose_name
        """
        l = mixer.blend(lessons.TrialLesson)
        self.assertIn('First', l.long_name_plural())

    def test_get_timeline_entries(self):
        teacher = create_teacher()
        lesson = mixer.blend(lessons.MasterClass, host=teacher)
        entry = mixer.blend(
            'timeline.Entry',
            teacher=teacher,
            lesson=lesson,
            start=self.tzdatetime(2032, 12, 10, 12, 0)
        )
        found = lesson.get_timeline_entries()
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0], entry)
