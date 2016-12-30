from datetime import timedelta
from unittest.mock import patch

from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer, create_teacher
from market.models import Subscription
from products.models import Product1


@freeze_time('2032-12-01 12:00')
class TestSUbscriptionUnit(TestCase):
    fixtures = ('products', 'lessons')

    @classmethod
    def setUpTestData(cls):
        cls.product = Product1.objects.get(pk=1)
        cls.product.duration = timedelta(days=5)
        cls.product.save()

        cls.customer = create_customer()

    def setUp(self):
        self.s = Subscription(
            customer=self.customer,
            product=self.product,
            buy_price=150
        )
        self.s.save()

    @patch('market.models.signals.class_scheduled.send')
    def _schedule(self, c, date, *args):
        c.timeline = mixer.blend(
            'timeline.Entry',
            lesson_type=c.lesson_type,
            teacher=create_teacher(),
            start=date,
        )
        c.save()

    def test_is_due(self):
        self.assertFalse(self.s.is_due())
        with freeze_time('2032-12-07 12:00'):  # move 6 days forward
            self.assertTrue(self.s.is_due())

    def test_update_first_lesson_date(self):
        first_class = self.s.classes.first()

        self._schedule(first_class, self.tzdatetime(2032, 12, 5, 13, 33))

        self.s.first_lesson_date = None  # set to None in case of first_class has set it up manualy — we check the subscription, not the class logic

        self.s.update_first_lesson_date()
        self.s.refresh_from_db()
        self.assertEqual(self.s.first_lesson_date, self.tzdatetime(2032, 12, 5, 13, 33))

    def test_update_first_lesson_uses_only_first_lesson(self):
        classes = self.s.classes.all()
        self._schedule(classes[0], self.tzdatetime(2032, 12, 5, 13, 33))
        self._schedule(classes[1], self.tzdatetime(2033, 12, 5, 13, 33))

        self.s.update_first_lesson_date()
        self.s.refresh_from_db()
        self.assertEqual(self.s.first_lesson_date, self.tzdatetime(2032, 12, 5, 13, 33))  # should be taken from the first class, not from the second
