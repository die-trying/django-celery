from datetime import datetime
from unittest.mock import Mock

from django.test import TestCase
from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import create_customer, create_teacher, mock_request
from hub.exceptions import CannotBeScheduled
from hub.models import Class, Subscription
from hub.scheduler import SortingHat
from products.models import Product1
from timeline.models import Entry as TimelineEntry


class TestScheduler(TestCase):
    fixtures = ('lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = create_customer()
        self.host = create_teacher()
        self.master_class = mixer.blend(lessons.MasterClass, host=self.host, slots=5)

    def get_the_hat(self, lesson_type=None, teacher=None, date='2016-01-01', time='13:37'):
        if lesson_type is None:
            lesson_type = lessons.OrdinaryLesson.get_contenttype().pk
        if teacher is None:
            teacher = self.host

        return SortingHat(
            customer=self.customer,
            lesson_type=lesson_type,
            teacher=teacher,
            date=date,
            time=time,
        )

    def _buy_a_lesson(self, lesson):
        c = Class(
            customer=self.customer,
            lesson=lesson
        )
        c.request = mock_request(self.customer)
        c.save()
        return c

    def _buy_a_subscription(self):
        product = Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.request = mock_request(self.customer)
        s.save()
        return s

    def test_set_err(self):
        s = self.get_the_hat()

        s._SortingHat__set_err('E_CLASS_NOT_FOUND')
        self.assertEquals(s.err, 'E_CLASS_NOT_FOUND')
        self.assertEquals(str(s.msg), "You don't have available lessons")

        s._SortingHat__set_err('NON_EXISTENT_ERR_TEXT')

        self.assertEquals(s.err, 'E_UNKNOWN')
        self.assertEquals(s.msg, 'Unknown scheduling error')

        self.assertFalse(s.result)
        s._SortingHat__set_err('E_NONE')
        self.assertTrue(s.result)

    def test_get_class_fail(self):
        s = self.get_the_hat()
        res = s._SortingHat__get_class()
        self.assertIsNone(res)

    def test_get_class_ok(self):
        s = self.get_the_hat()
        self._buy_a_lesson(lessons.OrdinaryLesson.get_default())
        res = s._SortingHat__get_class()
        self.assertIsInstance(res, Class)

    def test_find_entry_fail(self):
        s = self.get_the_hat(
            lesson_type=self.master_class.get_contenttype().pk
        )
        res = s._SortingHat__get_entry()
        self.assertIsNone(res)

    def test_find_entry_ok(self):
        s = self.get_the_hat(
            lesson_type=self.master_class.get_contenttype().pk
        )
        entry = TimelineEntry(
            teacher=self.host,
            lesson=self.master_class,
            start=datetime(2016, 1, 1, 13, 37)
        )
        entry.save()
        res = s._SortingHat__get_entry()
        self.assertEquals(res, entry)

    def test_find_entry_fail_due_to_slots(self):
        """
        Creates a timeline entry for fixtured Master Class lesson with 5 taken
        slots. The hat.__get_entry() should ignore it.
        """
        s = self.get_the_hat(
            lesson_type=self.master_class.get_contenttype().pk
        )
        entry = TimelineEntry(
            teacher=self.host,
            lesson=self.master_class,
            start=datetime(2016, 1, 1, 13, 37),
            taken_slots=5,  # fixtured master class defined only 5 slots
        )
        entry.save()
        res = s._SortingHat__get_entry()
        self.assertIsNone(res)  # all 5 slots of our timeline entry a planned, so should not return anything

    def test_find_a_class_err(self):
        s = self.get_the_hat()
        s._SortingHat__get_class = Mock(return_value=None)
        s.find_a_class()
        self.assertEquals(s.err, 'E_CLASS_NOT_FOUND')
        self.assertIn('curated session', s.msg)

    def test_find_a_class_ok(self):
        s = self.get_the_hat()
        s._SortingHat__get_class = Mock(return_value=100500)
        s.find_a_class()
        self.assertEquals(s.err, 'E_NONE')
        self.assertEquals(s.c, 100500)  # value from there ↑↑↑, duck typing rulez

    def test_find_an_entry_fail(self):
        s = self.get_the_hat(
            lesson_type=self.master_class.get_contenttype().pk
        )
        s._SortingHat__get_entry = Mock(return_value=None)
        s.find_an_entry()
        self.assertEquals(s.err, 'E_ENTRY_NOT_FOUND')

    def test_find_an_entry_for_lessons_that_dont_require_it(self):
        s = self.get_the_hat()  # by default the testing instance of the SortingHat searches for the Ordinary Lessons, that don't require a timeline entry
        mock = Mock(return_value=None)
        s._SortingHat__get_class = mock
        s.find_an_entry()
        mock.assert_not_called()

    def test_find_an_entry_ok(self):
        s = self.get_the_hat(
            lesson_type=self.master_class.get_contenttype().pk
        )
        s._SortingHat__get_entry = Mock(return_value=100500)
        s.find_an_entry()
        self.assertEquals(s.err, 'E_NONE')
        self.assertEquals(s.entry, 100500)  # value from there ↑↑↑, duck typing rulez

    def test_schedule_a_class_fail_with_entry(self):
        s = self.get_the_hat()
        s.entry = Mock()

        s.c = Mock()
        mocked_assign_entry = Mock(side_effect=CannotBeScheduled())
        s.c.assign_entry = mocked_assign_entry

        s.schedule_a_class()
        mocked_assign_entry.assert_called_with(s.entry)
        self.assertEquals(s.err, 'E_CANT_SCHEDULE')

    def test_schedule_a_class_fail_without_entry(self):
        s = self.get_the_hat()
        s.c = Mock()
        mocked_schedule = Mock(side_effect=CannotBeScheduled())
        s.c.schedule = mocked_schedule

        s.schedule_a_class()
        mocked_schedule.assert_called_with(date=datetime(2016, 1, 1, 13, 37), teacher=self.host)
        self.assertEquals(s.err, 'E_CANT_SCHEDULE')

    def test_get_only_active_classes(self):
        s = self.get_the_hat()
        lesson = lessons.OrdinaryLesson.get_default()
        entry = mixer.blend(TimelineEntry, lesson=lesson, teacher=self.host, active=1)
        c = self._buy_a_lesson(lesson)

        c.assign_entry(entry)
        c.save()

        res = s._SortingHat__get_class()
        self.assertIsNone(res)  # we already have scheduled the only class we could

    def test_get_the_subscription_class_first(self):
        """
        hat.__get_class() should return subscription lessons first.

        Buy a single lesson, then buy a subscription. Check, if get_class()
        would return a subscription lesson instead of single bought class.
        """
        s = self.get_the_hat()
        self._buy_a_lesson(lessons.OrdinaryLesson.get_default())
        subscription = self._buy_a_subscription()

        first_lesson_by_subscription = Class.objects.order_by('buy_date', 'id').filter(subscription=subscription)[0]

        res = s._SortingHat__get_class()
        self.assertEquals(res, first_lesson_by_subscription)

    def test_facade_fail(self):
        s = self.get_the_hat()
        mock = Mock(return_value=None)
        s.find_a_class = mock
        s.result = False
        self.assertFalse(s.do_the_thing())
        mock.assert_called_with()  # the first iteration of schedule() should happen

    def test_facade_ok(self):
        s = self.get_the_hat()
        mock = Mock(return_value=None)
        s.find_a_class = s.find_an_entry = s.schedule_a_class = mock
        self.assertTrue(s.do_the_thing())
        self.assertEquals(mock.call_count, 3)
