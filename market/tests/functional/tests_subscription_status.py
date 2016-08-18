from datetime import datetime

from django.test import TestCase

from elk.utils.testing import create_customer, create_teacher
from lessons import models as lessons
from market.models import Subscription
from products.models import Product1


class TestSubscriptionStatus(TestCase):
    fixtures = ('products', 'lessons')

    def setUp(self):
        self.customer = create_customer()
        self.teacher = create_teacher()
        self.subscription = Subscription(
            customer=self.customer,
            product=Product1.objects.get(pk=1),
            buy_price=150,
        )

        self.subscription.save()

    def _schedule(self, c, date=datetime(2032, 12, 1, 11, 30)):
        c.schedule(
            teacher=self.teacher,
            date=date,
            allow_besides_working_hours=True,
        )
        c.save()
        self.assertTrue(c.is_scheduled)
        return c

    def test_class_status_new(self):
        status = self.subscription.class_status()
        self.assertEqual(len(status), 5)

        ordinary_lessons_status = status[0]
        self.assertIn('Curated session', ordinary_lessons_status['name'])
        self.assertEqual(ordinary_lessons_status['used'], 0)
        self.assertEqual(ordinary_lessons_status['available'], 4)

        master_class_status = status[4]
        self.assertIn('Master Class', master_class_status['name'])
        self.assertEqual(master_class_status['used'], 0)
        self.assertEqual(master_class_status['available'], 1)

    def test_class_status_used(self):
        """
        Mark one class as used
        """
        c = self.subscription.classes.filter(lesson_type=lessons.OrdinaryLesson.get_contenttype()).first()
        c.mark_as_fully_used()
        status = self.subscription.class_status()
        ordinary_lessons_status = status[0]
        self.assertEqual(ordinary_lessons_status['used'], 1)
        self.assertEqual(ordinary_lessons_status['available'], 3)

    def test_class_scheduled(self):
        """
        Mark one class as scheduled
        """
        c = self.subscription.classes.filter(lesson_type=lessons.OrdinaryLesson.get_contenttype()).first()
        self._schedule(c)
        status = self.subscription.class_status()
        ordinary_lessons_status = status[0]
        self.assertEqual(ordinary_lessons_status['used'], 0)
        self.assertEqual(ordinary_lessons_status['available'], 4)
        self.assertEqual(ordinary_lessons_status['scheduled'], 1)
