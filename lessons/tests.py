import json
from datetime import timedelta

from django.core.exceptions import ValidationError
from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import ClientTestCase, TestCase, create_teacher
from lessons.api.serializers import factory as lessons_serializer_factory


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
        self.assertIn('Curated', str(l.long_name))

    def test_long_name_from_verbose_name(self):
        """
        Trial lessons don't defined custom long name but still have one from verbose_name
        """
        l = mixer.blend(lessons.TrialLesson)
        self.assertIn('First', str(l.long_name))

    def test_long_name_plural(self):
        l = mixer.blend(lessons.OrdinaryLesson)
        self.assertIn('Curated lessons', str(l.long_name_plural))

    def test_long_name_plural_from_verbose_name(self):
        """
        Trial lessons don't defined custom long name but still have one from verbose_name
        """
        l = mixer.blend(lessons.TrialLesson)
        self.assertIn('First', str(l.long_name_plural))

    # def test_assure_slot_count(self):
    #     l = mixer.blend(lessons.OrdinaryLesson)
    #     l.available_slots_count = 100500
    #     result = l.as_dict()
    #     self.assertEqual(result['available_slots_count'], 100500)


class TestLessonSerializers(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.teacher = create_teacher()

    def test_factory_hosted_lesson(self):
        master_class = mixer.blend('lessons.MasterClass', host=self.teacher)
        Serializer = lessons_serializer_factory(master_class)

        serialized = Serializer(master_class).data

        self.assertEqual(serialized['name'], master_class.name)

    def test_factory_non_hosted_lesson(self):
        ordinary_lesson = mixer.blend('lessons.OrdinaryLesson')
        Serializer = lessons_serializer_factory(ordinary_lesson)

        serialized = Serializer(ordinary_lesson).data

        self.assertEqual(serialized['name'], ordinary_lesson.name)

    def test_serializer_fields(self):
        master_class = mixer.blend(
            'lessons.MasterClass',
            host=self.teacher,
            announce='*test*',
            duration=timedelta(minutes=30),
        )
        Serializer = lessons_serializer_factory(master_class)

        serialized = Serializer(master_class).data

        self.assertEqual(serialized['host'], self.teacher.user.crm.full_name)  # should serialize lesson host
        self.assertIn('<em>test</em>', serialized['announce'])  # markdown should be rendered
        self.assertEqual(serialized['duration'], '00:30:00')


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
