from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from lessons import models as lessons
from teachers import models

_planning_ofsset = models._planning_ofsset


class TestTeacherUnit(TestCase):
    def setUp(self):
        models.PLANNING_DELTA = timedelta(hours=2)

    def test_timeline_url(self):
        teacher = create_teacher()
        self.assertEqual(teacher.timeline_url(), '/timeline/%s/' % teacher.user.username)

    def test_absolute_url(self):
        teacher = create_teacher()
        self.assertEqual(teacher.get_absolute_url(), '/teachers/%s/' % teacher.user.username)

    @freeze_time('2032-05-03 13:00')
    def test_planning_offset(self):
        late_start = self.tzdatetime(2032, 5, 5, 13, 0)
        self.assertEqual(_planning_ofsset(late_start), late_start)

        early_start = self.tzdatetime(2032, 5, 1, 13, 0)
        self.assertEqual(_planning_ofsset(early_start), self.tzdatetime('UTC', 2032, 5, 3, 15, 00))  # +2 hours from now

    def test_planning_offset_roundup(self):
        """
        Check if planning offset rounds the time up
        """
        start = self.tzdatetime(2032, 5, 1, 13, 0)

        with freeze_time('2032-05-03 13:25'):
            self.assertEqual(_planning_ofsset(start), self.tzdatetime('UTC', 2032, 5, 3, 15, 30))  # shoud round to 15:30

        with freeze_time('2032-05-03 13:45'):
            self.assertEqual(_planning_ofsset(start), self.tzdatetime('UTC', 2032, 5, 3, 16, 0))  # shoud round to 16:00

        with freeze_time('2032-05-03 21:45'):
            self.assertEqual(_planning_ofsset(start), self.tzdatetime('UTC', 2032, 5, 4, 0, 0))  # should move to the next day

        with freeze_time('2032-05-03 12:00'):
            self.assertEqual(_planning_ofsset(start), self.tzdatetime('UTC', 2032, 5, 3, 14, 0))  # no roundup


class TestTeacherAvaliableLessons(TestCase):
    fixtures = ('lessons',)

    def setUp(self):
        self.teacher = create_teacher(accepts_all_lessons=False)

    def test_hosted_lessons_ok(self):
        self.teacher.allowed_lessons.add(lessons.MasterClass.get_contenttype())
        master_class = mixer.blend(lessons.MasterClass, host=self.teacher)

        res = self.teacher.available_lessons(lesson_type=lessons.MasterClass.get_contenttype())
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], master_class)

    def test_hosted_lessons_fail_due_to_another_teacher(self):
        another_teacher = create_teacher()
        another_teacher.allowed_lessons.add(lessons.MasterClass.get_contenttype())

        mixer.blend(lessons.MasterClass, host=another_teacher)
        res = self.teacher.available_lessons(lesson_type=lessons.MasterClass.get_contenttype())

        self.assertEqual(len(res), 0)

    def test_unhosted_lessons_ok(self):
        self.teacher.allowed_lessons.add(lessons.OrdinaryLesson.get_contenttype())
        self.teacher.save()

        res = self.teacher.available_lessons(lesson_type=lessons.OrdinaryLesson.get_contenttype())
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].get_contenttype(), lessons.OrdinaryLesson.get_contenttype())

    def test_unhosted_lessons_fail_due_to_no_permission(self):
        mixer.blend(lessons.OrdinaryLesson)
        res = self.teacher.available_lessons(lesson_type=lessons.OrdinaryLesson.get_contenttype())

        self.assertEqual(len(res), 0)


class TestTeacherAvailableLessonTypes(TestCase):
    fixtures = ('lessons',)

    def setUp(self):
        self.teacher = create_teacher(accepts_all_lessons=False)

    def test_allowed_lesson_types_empty(self):
        res = list(self.teacher.available_lesson_types())
        self.assertEquals(len(res), 0)  # should not throw anything

    def test_allowed_lesson_types_non_lessons_bypass(self):
        """
        Allow teacher to host somethind from lessons.models that is not a lesson
        """
        self.teacher.allowed_lessons.add(ContentType.objects.get_for_model(lessons.Language))

        res = list(self.teacher.available_lesson_types())
        self.assertEquals(len(res), 0)  # should not throw anything

    def test_allowed_lessons_types_non_hosted(self):
        """
        Allow teacher to host curated sessions
        """
        self.teacher.allowed_lessons.add(lessons.OrdinaryLesson.get_contenttype())

        res = list(self.teacher.available_lesson_types())
        self.assertEqual(len(res), 1)

    def test_allowed_lessons_types_non_hosted_fail_due_to_no_lessons(self):
        """
        Allow teacher to host master classes, but don't create lessons to host —
        should not return anything.
        """
        self.teacher.allowed_lessons.add(lessons.MasterClass.get_contenttype())

        res = list(self.teacher.available_lesson_types())
        self.assertEqual(len(res), 0)

    def test_allowed_lesson_types_non_hosted_ok(self):
        self.teacher.allowed_lessons.add(lessons.MasterClass.get_contenttype())

        mixer.blend(lessons.MasterClass, host=self.teacher)
        res = list(self.teacher.available_lesson_types())
        self.assertEqual(len(res), 1)

    def test_allowed_lesson_sort_order(self):
        """
        Allowed content types should be returned in order defined in lessons.models
        """
        self.teacher.allowed_lessons.add(lessons.MasterClass.get_contenttype())
        self.teacher.allowed_lessons.add(lessons.OrdinaryLesson.get_contenttype())

        mixer.blend(lessons.MasterClass, host=self.teacher)
        res = list(self.teacher.available_lesson_types())

        self.assertEqual(len(res), 2)

        self.assertEqual(res[0], lessons.OrdinaryLesson.get_contenttype())
        self.assertEqual(res[1], lessons.MasterClass.get_contenttype())
