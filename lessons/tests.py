import json

from django.core.exceptions import ValidationError
from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import ClientTestCase, TestCase, create_teacher


class TestLessonsUnit(TestCase):
    def test_planning_unaccaptable_lesson(self):
        lazy_teacher = create_teacher(accepts_all_lessons=False)  # teacher2 does not accept any lesson, so cannot be planned
        hard_working_teacher = create_teacher()

        with self.assertRaises(ValidationError):
            mixer.blend(lessons.MasterClass, host=lazy_teacher)

        self.assertIsNotNone(mixer.blend(lessons.MasterClass, host=hard_working_teacher))

    def test_admin_url(self):
        l = mixer.blend(lessons.MasterClass, host=create_teacher())
        self.assertIn(str(l.pk), l.admin_url)
        self.assertIn('admin/lessons/masterclass', l.admin_url)

    def test_type_verbose_name(self):
        l = mixer.blend(lessons.OrdinaryLesson)
        self.assertIn('single', str(l.type_verbose_name))

    def test_assure_markdown_is_rendered(self):
        l = mixer.blend(lessons.OrdinaryLesson, description='**bold**')
        result = l.as_dict()
        self.assertIn('<strong>bold</strong>', result['description'])

    def test_assure_slot_count(self):
        l = mixer.blend(lessons.OrdinaryLesson)
        l.available_slots_count = 100500
        result = l.as_dict()
        self.assertEqual(result['available_slots_count'], 100500)


class TestLessonsFunctional(ClientTestCase):
    def setUp(self):
        self.teacher = create_teacher()

    def testAvailableLessonsJSON(self):
        """
        Fetch JSON with lessons of certain type, available to generated user
        """
        for lesson in (lessons.OrdinaryLesson, lessons.MasterClass, lessons.HappyHour):
            self.__test_lesson(lesson)

    def __test_lesson(self, klass):
        mocked_lessons = {}

        for i in range(0, 55):
            mocked_lesson = mixer.blend(klass, host=self.teacher)
            mocked_lessons[mocked_lesson.pk] = mocked_lesson

        lesson_type_id = klass.get_contenttype().pk

        response = self.c.get('/lessons/%s/type/%d/available.json' % (self.teacher.user.username, lesson_type_id))

        self.assertEquals(response.status_code, 200)
        got_lessons = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(got_lessons), 55)

        for i in got_lessons:
            mocked_lesson = mocked_lessons[i['id']]
            self.assertEqual(i['name'], mocked_lesson.name)
            self.assertEqual(i['duration'], str(mocked_lesson.duration))
            self.assertEqual(i['required_slots'], mocked_lesson.slots)
