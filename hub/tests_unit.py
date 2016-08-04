from datetime import datetime
from unittest.mock import MagicMock

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from mixer.backend.django import mixer

import lessons.models as lessons
import products.models as products
from elk.utils.testing import create_customer, create_teacher
from hub import signals
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
        s.save()

        self.assertEqual(s.name_for_user, product.name)

    def test_single_class_name(self):
        lesson = products.OrdinaryLesson.get_default()
        c = Class(
            customer=self.customer,
            lesson=lesson
        )
        c.save()

        self.assertEqual(c.name_for_user, lesson.name)

    def test_no_deletion(self):
        """
        No buyable product can ever be deleted.
        """
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150
        )
        s.save()
        self.assertEqual(s.active, 1)
        s.delete()
        s.refresh_from_db()
        self.assertEqual(s.active, 0)


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
        s.save()

    def _schedule(self, lesson_type=None, date=datetime(2032, 12, 1, 11, 30)):  # By default it will fail in 16 years, sorry
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

    def test_deletion_of_a_scheduled_class(self):
        """
        Deletion of a scheduled class should just call it's
        unscheduling mechanism.
        """
        c = self._buy_a_lesson()
        entry = mixer.blend(TimelineEntry, slots=1, lesson=self.lesson, teacher=self.teacher)
        c.assign_entry(entry)
        c.save()

        unschedule = MagicMock(return_value=True)
        c.unschedule = unschedule
        c.delete()

        c.refresh_from_db()
        unschedule.assert_any_call()

    def test_deletion_of_an_unscheduled_class(self):
        """
        Deletion of an unscheduled class should be like any other
        :model:`hub.BuyableProduct`.
        """
        c = self._buy_a_lesson()
        unschedule = MagicMock(return_value=True)
        c.unschedule = unschedule

        c.delete()
        c.refresh_from_db()

        unschedule.assert_not_called()
        self.assertEqual(c.active, 0)


class TestClassSignals(TestCase):
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
        c.save()
        return c

    def _schedule(self, c, date=datetime(2032, 12, 1, 11, 30)):  # By default it will fail in 16 years, sorry
        c.schedule(
            teacher=self.teacher,
            date=date,
            allow_besides_working_hours=True,
        )
        c.save()
        self.assertTrue(c.is_scheduled)
        return c

    def _test_scheduled_class_signal(self):
        handler = MagicMock()
        c = self._buy_a_lesson()
        signals.class_scheduled.connect(handler)
        self._schedule(c)
        self.assertEqual(handler.call_count, 1)
        return [c, handler]

    def test_scheduled_class_signal_called_once(self):
        [c, handler] = self._test_scheduled_class_signal()
        c.save()  # signal is emited during the save() method, so let's call it one more time
        self.assertEqual(handler.call_count, 1)

    def _test_unscheduled_class_signal(self):
        handler = MagicMock()
        c = self._buy_a_lesson()
        signals.class_unscheduled.connect(handler)
        self._schedule(c)
        c.unschedule()
        self.assertEqual(handler.call_count, 0)  # assert that signal is not emited during the unschedule, because it can fail
        c.save()
        self.assertEqual(handler.call_count, 1)
        return [c, handler]

    def test_unscheduled_class_signal_called_once(self):
        [c, handler] = self._test_unscheduled_class_signal()
        c.save()  # signal is emited during the save() method, so let's call it one more time
        self.assertEqual(handler.call_count, 1)
