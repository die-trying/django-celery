from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from lessons import models as lessons


class TestTeacherFunctional(TestCase):
    fixtures = ('crm', 'teachers', 'lessons')

    def setUp(self):
        self.teacher = create_teacher(accepts_all_lessons=False)

    def test_automatic_group_assignment(self):
        """
        All newly created teachers should be members of 'teacher' permission group
        """
        from teachers.models import TEACHER_GROUP_ID
        self.assertEqual(self.teacher.user.groups.first().pk, TEACHER_GROUP_ID)

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
