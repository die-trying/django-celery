import json

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.test import test_teacher


class TestLessonsFunctional(TestCase):
    def setUp(self):
        self.teacher = test_teacher()
        self.c = Client()

        self.superuser = User.objects.create_superuser('root', 'te@ss.tt', '123')
        self.c.login(username='root', password='123')

    def testAvailableLessonsJSON(self):
        """
        Fetch JSON with lessons of certain type, available to generated user
        """
        for lesson in (lessons.OrdinaryLesson, lessons.MasterClass, lessons.HappyHour):
            self.__test_lesson_JSON(lesson)

    def __test_lesson_JSON(self, klass):
        mocked_lessons = {}

        for i in range(0, 55):
            mocked_lesson = mixer.blend(klass, host=self.teacher)
            mocked_lessons[mocked_lesson.pk] = mocked_lesson

        lesson_type_id = ContentType.objects.get_for_model(klass).pk

        response = self.c.get('/lessons/%s/available.json?lesson_id=%d' % (self.teacher.user.username, lesson_type_id))

        self.assertEquals(response.status_code, 200)
        got_lessons = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(got_lessons), 55)

        for i in got_lessons:
            mocked_lesson = mocked_lessons[i['id']]
            self.assertEqual(i['name'], mocked_lesson.internal_name)
            self.assertEqual(i['duration'], str(mocked_lesson.duration))
            self.assertEqual(i['slots'], mocked_lesson.slots)
