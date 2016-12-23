from datetime import timedelta

from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from lessons.api.serializers import factory as lessons_serializer_factory


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
