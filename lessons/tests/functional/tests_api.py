import json

from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import ClientTestCase, create_teacher


class TestLessonsAPI(ClientTestCase):
    fixtures = ('lessons',)

    def setUp(self):
        self.teacher = create_teacher()

    def test_non_hosted_lessons_json(self):
        """
        Fetch JSON with non-hosted lessons, available to the generated teacher
        """
        lesson_type = lessons.OrdinaryLesson.get_contenttype()

        response = self.c.get('/api/teachers/{teacher_id}/available_lessons.json?lesson_type={lesson_type_id}'.format(
            teacher_id=self.teacher.pk,
            lesson_type_id=lesson_type.pk,
        ))

        self.assertEquals(response.status_code, 200)

        got_lessons = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(got_lessons), 1)

    def test_non_hosted_lesson_passed_other_lessons(self):
        """
        Check, if non-hosted lessons output bypasses non-default non-hosted lessons
        """
        for i in range(0, 5):
            mixer.blend(lessons.OrdinaryLesson)

        # copy-paste from previous test
        lesson_type = lessons.OrdinaryLesson.get_contenttype()

        response = self.c.get('/api/teachers/{teacher_id}/available_lessons.json?lesson_type={lesson_type_id}'.format(
            teacher_id=self.teacher.pk,
            lesson_type_id=lesson_type.pk,
        ))

        self.assertEquals(response.status_code, 200)

        got_lessons = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(got_lessons), 1)
        # copy-paste end

        default_lesson = lessons.OrdinaryLesson.get_default()

        got_lesson = got_lessons[0]

        self.assertEqual(got_lesson['id'], default_lesson.pk)

    def test_hosted_lessons_json(self):
        """
        Fetch JSON with hosted lessons, available to the generated teacher
        """
        for klass in (lessons.MasterClass, lessons.HappyHour):
            mocked_lessons = {}
            for i in range(0, 5):
                mocked_lesson = mixer.blend(klass, host=self.teacher)
                mocked_lessons[mocked_lesson.pk] = mocked_lesson

            lesson_type_id = klass.get_contenttype().pk

            response = self.c.get('/api/teachers/{teacher_id}/available_lessons.json?lesson_type={lesson_type_id}'.format(
                teacher_id=self.teacher.pk,
                lesson_type_id=lesson_type_id,
            ))

            self.assertEquals(response.status_code, 200)
            got_lessons = json.loads(response.content.decode('utf-8'))

            self.assertEqual(len(got_lessons), 5)

            for i in got_lessons:
                mocked_lesson = mocked_lessons[i['id']]
                self.assertEqual(i['name'], mocked_lesson.name)
                self.assertEqual(i['id'], mocked_lesson.pk)
