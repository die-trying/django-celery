from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market.exceptions import CannotBeUnscheduled
from market.models import Class, Subscription
from products import models as products


class TestClassManager(TestCase):
    fixtures = ('lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = create_customer()
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        self.subscription = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        self.subscription.save()

    def _schedule(self, lesson_type=None, date=datetime(2032, 12, 1, 11, 30)):  # By default it will fail in 16 years, sorry
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        if lesson_type is None:
            lesson_type = lessons.OrdinaryLesson.get_contenttype()
        c = self.customer.classes.filter(lesson_type=lesson_type, is_scheduled=False).first()
        """
        If this test will fail when you change the SortingHat behaviour, just
        replace the above lines with the SortingHat invocation
        """
        c.schedule(
            teacher=create_teacher(),
            date=date,
            allow_besides_working_hours=True,
        )
        c.save()
        self.assertTrue(c.is_scheduled)
        return c

    def test_nearest_scheduled_ok(self):
        c = self._schedule()
        c1 = self.customer.classes.nearest_scheduled()
        self.assertEqual(c1, c)

    def test_nearest_scheduled_ordering(self):
        c2 = self._schedule(date=datetime(2020, 12, 1, 11, 30))
        self._schedule(date=datetime(2032, 12, 1, 11, 30))

        c_found = self.customer.classes.nearest_scheduled()
        self.assertEquals(c_found, c2)

    def test_nearest_scheduled_fail(self):
        """
        Run without any scheduled class
        """
        c = self._schedule()
        c.unschedule()
        c.save()

        self.assertIsNone(self.customer.classes.nearest_scheduled())  # should not throw anything

    def test_starting_soon(self):
        self._schedule()
        with patch('market.models.ClassesManager._ClassesManager__now') as mocked_date:
            mocked_date.return_value = timezone.make_aware(datetime(2032, 12, 1, 10, 0))
            self.assertEquals(self.customer.classes.starting_soon(timedelta(minutes=89)).count(), 0)
            self.assertEquals(self.customer.classes.starting_soon(timedelta(minutes=91)).count(), 1)

    def test_nearest_dont_return_past_classes(self):
        """
        Test if clases.nearest_scheduled() does not return classes in the past
        """
        self._schedule(date=datetime(2020, 12, 1, 11, 30))
        c2 = self._schedule(date=datetime(2032, 12, 1, 11, 30))
        c_found = self.customer.classes.nearest_scheduled(date=datetime(2025, 12, 1, 11, 30))  # 5 years later, then the fist sccheduled class
        self.assertEquals(c_found, c2)

    def test_available_lesson_types(self):
        lesson_types = self.customer.classes.bought_lesson_types()
        self.assertEquals(len(lesson_types), 5)  # if you have defined a new lesson, fill free to increase this value, it's ok

        self.assertIn(lessons.OrdinaryLesson.get_contenttype(), lesson_types)
        self.assertIn(lessons.MasterClass.get_contenttype(), lesson_types)

    def test_lesson_type_sorting(self):  # noqa
        """
        Planning dates should be sorted with the in-class defined sort order
        """
        lesson_types = self.customer.classes.bought_lesson_types()

        sort_order = {}
        for m in ContentType.objects.filter(app_label='lessons'):
            Model = m.model_class()
            if not hasattr(Model, 'sort_order'):  # non-sortable models are possibly not lessons
                continue

            order = Model.sort_order()
            if order:
                sort_order[order] = Model

        sorted_lessons = []
        for i in sorted(list(sort_order.keys())):
            sorted_lessons.append(sort_order[i])

        for lesson_type in lesson_types:
            ordered_lesson = sorted_lessons.pop(0)
            self.assertEquals(lesson_type.model_class(), ordered_lesson)

    def test_find_student_classes_nothing(self):
        self.subscription.delete()
        no_students = Class.objects.find_student_classes(lesson_type=lessons.OrdinaryLesson.get_contenttype())
        self.assertEquals(len(no_students), 0)

    def test_find_student_classes(self):
        single = Class.objects.find_student_classes(lesson_type=lessons.OrdinaryLesson.get_contenttype())
        self.assertEqual(single[0].customer, self.customer)

    def test_dates_for_planning(self):
        dates = [i for i in self.customer.classes.dates_for_planning()]
        self.assertEquals(len(dates), 7)  # should return seven next days

        for i in dates:
            self.assertIsInstance(i, datetime)

        self.assertEquals(dates[0].strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'))  # the first day should be today

    def test_to_be_marked_as_used_fail(self):
        no_classes = Class.objects.to_be_marked_as_used()
        self.assertEquals(len(no_classes), 0)

    def test_to_be_marked_as_used_fail_on_used(self):
        c = self._schedule(date=datetime(2016, 12, 1, 15, 0))
        c.mark_as_fully_used()

        with patch('market.models.ClassesManager._ClassesManager__now') as mocked_date:
            mocked_date.return_value = timezone.make_aware(datetime(2016, 12, 1, 15, 30))
            no_classes = Class.objects.to_be_marked_as_used()
            self.assertEquals(len(no_classes), 0)

    def test_to_be_marked_as_used_fail_on_future(self):
        self._schedule(date=datetime(2016, 12, 1, 15, 0))
        with patch('market.models.ClassesManager._ClassesManager__now') as mocked_date:
            mocked_date.return_value = timezone.make_aware(datetime(2016, 12, 1, 14, 00))  # 1,5 hours before the class finish
            no_classes = Class.objects.to_be_marked_as_used()
            self.assertEquals(len(no_classes), 0)

    def test_to_be_marked_as_used_ok(self):
        c = self._schedule(date=datetime(2016, 12, 1, 15, 0))
        with patch('market.models.ClassesManager._ClassesManager__now') as mocked_date:
            mocked_date.return_value = timezone.make_aware(datetime(2016, 12, 1, 16, 31))
            classes = Class.objects.to_be_marked_as_used()
            self.assertLessEqual(1, mocked_date.call_count)
            self.assertEqual(len(classes), 1)
            self.assertEqual(classes[0], c)

    def test_cant_unschedule_in_past(self):
        c = self._schedule(date=timezone.make_aware(datetime(2020, 12, 1, 11, 30)))
        c.timeline.is_in_past = MagicMock(return_value=True)
        with self.assertRaises(CannotBeUnscheduled):
            c.unschedule()

    def test_mark_as_fully_used(self):
        c = self._schedule()
        c.mark_as_fully_used()
        c.refresh_from_db()
        self.assertTrue(c.is_fully_used)

    def test_renew(self):
        c = self._schedule()
        c.mark_as_fully_used()
        c.save()
        self.assertTrue(c.is_fully_used)
        self.assertIsNotNone(c.timeline)

        c.renew()
        c.save()

        self.assertFalse(c.is_fully_used)
        self.assertIsNone(c.timeline)
