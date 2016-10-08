from elk.utils.testing import TestCase
from lessons import models as lessons
from products.models import Product1


class TestSubscriptionDisplayTestCase(TestCase):
    fixtures = ('crm', 'lessons', 'products')

    def setUp(self):
        self.product = Product1.objects.get(pk=1)

    def test_lesson_types(self):
        lesson_types = list(self.product.lesson_types())
        self.assertEqual(len(lesson_types), 5)
        self.assertEqual(lesson_types[0], lessons.OrdinaryLesson.get_contenttype())
        self.assertEqual(lesson_types[4], lessons.MasterClass.get_contenttype())

    def test_lessons(self):
        bundled_lessons = list(self.product.lessons())
        self.assertEqual(len(bundled_lessons), 5)
        self.assertEqual(bundled_lessons[0].first().get_contenttype(), lessons.OrdinaryLesson.get_contenttype())
        self.assertEqual(bundled_lessons[4].first().get_contenttype(), lessons.MasterClass.get_contenttype())

    def test_classes_by_lesson_type(self):
        ordinary_lesson_type = lessons.OrdinaryLesson.get_contenttype()
        master_class_type = lessons.MasterClass.get_contenttype()

        ordinary_lessons = self.product.classes_by_lesson_type(ordinary_lesson_type)
        master_classes = self.product.classes_by_lesson_type(master_class_type)

        self.assertEqual(len(ordinary_lessons), 5)  # fill free to modify this if you've changed the first subcription
        self.assertEqual(len(master_classes), 1)
