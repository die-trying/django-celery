from elk.utils.testing import TestCase, create_teacher
from lessons import models as lessons
from teachers.models import Teacher


class TeacherManagerTestCase(TestCase):
    def setUp(self):
        self.teacher = create_teacher(works_24x7=True, accepts_all_lessons=False)

    def test_filter_by_lesson_type_none(self):
        lesson_type = lessons.OrdinaryLesson.get_contenttype()
        res = Teacher.objects.by_lesson_type(lesson_type)

        self.assertEqual(len(res), 0)

    def test_filter_by_lesson_type_ok(self):

        lesson_type = lessons.OrdinaryLesson.get_contenttype()
        self.teacher.allowed_lessons.add(lesson_type)

        res = Teacher.objects.by_lesson_type(lesson_type)

        self.assertEqual(res.first(), self.teacher)

    def test_with_foto_none(self):
        self.teacher.teacher_photo = ''
        self.teacher.save()

        res = Teacher.objects.with_photos()

        self.assertEqual(len(res), 0)

    def test_with_foto_ok(self):
        res = Teacher.objects.with_photos()

        self.assertEqual(res.first(), self.teacher)
