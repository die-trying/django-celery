from datetime import datetime
from unittest.mock import MagicMock

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from mixer.backend.django import mixer

import lessons.models as lessons
import products.models as products
from elk.utils.testing import create_customer, create_teacher, mock_request
from hub.models import Class, Subscription
from timeline.models import Entry as TimelineEntry


class testBuyableProduct(TestCase):
    fixtures = ('crm', 'lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = create_customer()

    def test_subscription_name(self):
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.request = mock_request(self.customer)
        s.save()

        self.assertEqual(s.name_for_user, product.name)

    def test_single_class_name(self):
        lesson = products.OrdinaryLesson.get_default()
        c = Class(
            customer=self.customer,
            lesson=lesson
        )
        c.request = mock_request(self.customer)
        c.save()

        self.assertEqual(c.name_for_user, lesson.name)


class TestClassManager(TestCase):
    fixtures = ('lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = create_customer()
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.request = mock_request()
        s.save()

    def test_available_lesson_types(self):
        lesson_types = self.customer.classes.bought_lesson_types()
        self.assertEquals(len(lesson_types), 4)  # if you have defined a new lesson, fill free to increase this value, it's ok

        self.assertIn(lessons.OrdinaryLesson.contenttype(), lesson_types)
        self.assertIn(lessons.MasterClass.contenttype(), lesson_types)

    def test_lesson_type_sorting(self):
        """
        Planning dates should be sorted with the in-class defined sort order
        """
        lesson_types = self.customer.classes.bought_lesson_types()

        sort_order = {}
        for m in ContentType.objects.filter(app_label='lessons'):
            Model = m.model_class()
            order = Model.sort_order()
            if order:
                sort_order[order] = Model

        sorted_lessons = []
        for i in sorted(list(sort_order.keys())):
            sorted_lessons.append(sort_order[i])

        for lesson_type in lesson_types:
            ordered_lesson = sorted_lessons.pop(0)
            self.assertEquals(lesson_type.model_class(), ordered_lesson)

    def test_dates_for_planning(self):
        dates = [i for i in self.customer.classes.dates_for_planning()]
        self.assertEquals(len(dates), 7)  # should return seven next days

        for i in dates:
            self.assertIsInstance(i, datetime)

        self.assertEquals(dates[0].strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'))  # the first day should be today


class TestNoTimelinePoluting(TestCase):
    """
    This test suite tests, that class schedule method do not polute any teacher's
    timeline till the class is saved
    """
    fixtures = ('lessons',)

    def setUp(self):
        self.customer = create_customer()
        self.teacher = create_teacher()
        self.lesson = lessons.OrdinaryLesson.get_default()

    def _buy_a_lesson(self):
        c = Class(
            customer=self.customer,
            lesson=self.lesson
        )
        c.request = mock_request(self.customer)
        c.save()
        return c

    def test_schedule_entry(self):
        """ Not poluting timeline with existing timeline entries """
        c = self._buy_a_lesson()
        entry = mixer.blend(TimelineEntry, slots=1, lesson=self.lesson, teacher=self.teacher)
        entry.save = MagicMock(return_value=None)

        c.schedule_entry(entry)

        entry.save.assert_not_called()

    def test_schedule_auto_entry(self):
        """ Not poluting timeline when generating timeline entry """
        c = self._buy_a_lesson()
        c.schedule(
            teacher=self.teacher,
            date=datetime(2016, 12, 1, 0, 15)
        )
        self.assertIsNone(c.timeline_entry.pk)
        c.timeline_entry.save = MagicMock(return_value=None)
        c.timeline_entry.save.assert_not_called()


class TestTryToSchedule(TestCase):
    fixtures = ('lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = create_customer()
        self.host = create_teacher()

    def _buy_a_lesson(self, lesson):
        c = Class(
            customer=self.customer,
            lesson=lesson
        )
        c.request = mock_request(self.customer)
        c.save()
        return c

    def _buy_a_subscription(self):
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.request = mock_request(self.customer)
        s.save()
        return s

    def test_find_class(self):
        res = Class.objects.find_class(
            customer=self.customer,
            lesson_type=lessons.OrdinaryLesson.contenttype()
        )
        self.assertFalse(res['result'])
        self.assertEquals(res['error'], 'E_CLASS_NOT_FOUND')
        self.assertIn('curated session', res['text'])  # err text should contain name of the lesson

        self._buy_a_lesson(lessons.OrdinaryLesson.get_default())
        res = Class.objects.find_class(
            customer=self.customer,
            lesson_type=lessons.OrdinaryLesson.contenttype()
        )
        self.assertTrue(res['result'])  # should find now
        self.assertIsInstance(res['class'], Class)

    def test_find_only_active_classes(self):
        lesson = lessons.OrdinaryLesson.get_default()
        entry = mixer.blend(TimelineEntry, lesson=lesson, teacher=self.host, active=1)
        c = self._buy_a_lesson(lesson)

        c.schedule_entry(entry)
        c.save()

        res = Class.objects.find_class(
            customer=self.customer,
            lesson_type=lessons.OrdinaryLesson.contenttype()
        )
        self.assertFalse(res['result'])  # we already have scheduled the only class we could

    def test_find_the_subscription_class_first(self):
        """
        Return subscription lessons first.

        Buy a single lesson, than buy a subscription an check, that find_class()
        would return a subscription lesson.
        """
        self._buy_a_lesson(lessons.OrdinaryLesson.get_default())
        subscription = self._buy_a_subscription()

        first_lesson_by_subscription = Class.objects.order_by('buy_date', 'id').filter(subscription=subscription)[0]

        res = Class.objects.find_class(
            customer=self.customer,
            lesson_type=lessons.OrdinaryLesson.contenttype()
        )
        self.assertTrue(res['result'])
        self.assertEquals(res['class'], first_lesson_by_subscription)
