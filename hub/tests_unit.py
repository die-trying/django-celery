from datetime import datetime
from unittest.mock import MagicMock

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from mixer.backend.django import mixer

import lessons.models as lessons
import products.models as products
from elk.utils.testing import create_customer, create_teacher, mock_request
from hub.exceptions import CannotBeScheduled
from hub.models import Class, Subscription
from teachers.models import WorkingHours
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

        self.assertIn(lessons.OrdinaryLesson.get_contenttype(), lesson_types)
        self.assertIn(lessons.MasterClass.get_contenttype(), lesson_types)

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


class TestScheduleLowLevel(TestCase):
    fixtures = ('lessons',)

    def setUp(self):
        self.customer = create_customer()
        self.teacher = create_teacher()
        self.lesson = lessons.OrdinaryLesson.get_default()
        mixer.blend(WorkingHours, teacher=self.teacher, weekday=0, start='13:00', end='15:00')  # monday

    def _buy_a_lesson(self):
        c = Class(
            customer=self.customer,
            lesson=self.lesson
        )
        c.request = mock_request(self.customer)
        c.save()
        return c

    def test_assign_entry(self):
        """ Not poluting timeline with existing timeline entries """
        c = self._buy_a_lesson()
        entry = mixer.blend(TimelineEntry, slots=1, lesson=self.lesson, teacher=self.teacher)
        entry.save = MagicMock(return_value=None)

        c.assign_entry(entry)

        entry.save.assert_not_called()

    def test_schedule_auto_entry(self):
        """ Not poluting timeline when generating timeline entry """
        c = self._buy_a_lesson()
        c.schedule(
            teacher=self.teacher,
            date=datetime(2016, 12, 1, 7, 25),  # monday
            allow_besides_working_hours=True,
        )
        self.assertIsNone(c.timeline_entry.pk)
        c.timeline_entry.save = MagicMock(return_value=None)
        c.timeline_entry.save.assert_not_called()

    def test_schedule_auto_entry_only_within_working_hours(self):
        c = self._buy_a_lesson()
        with self.assertRaises(CannotBeScheduled):
            c.schedule(
                teacher=self.teacher,
                date=datetime(2016, 12, 1, 7, 27)  # wednesday
            )
            c.save()
