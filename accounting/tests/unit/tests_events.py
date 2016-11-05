from mixer.backend.django import mixer

from accounting.models import Event as AccEvent
from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market.models import Class
from market.sortinghat import SortingHat
from timeline.models import Entry as TimelineEntry


class TestEventOriginatorProperties(TestCase):
    fixtures = ('lessons',)

    def setUp(self):
        self.host = create_teacher(works_24x7=True)
        self.customer = create_customer()
        self.lesson = lessons.OrdinaryLesson.get_default()

        self.c = self._buy_a_lesson()
        self.entry = self._create_entry()
        self._schedule()

    def _buy_a_lesson(self, customer=None):
        if customer is None:
            customer = self.customer
        c = Class(
            customer=customer,
            lesson_type=self.lesson.get_contenttype(),
        )
        c.save()
        self.assertFalse(c.is_fully_used)
        self.assertFalse(c.is_scheduled)
        return c

    def _create_entry(self):
        entry = mixer.blend(
            TimelineEntry,
            slots=1,
            lesson=self.lesson,
            teacher=self.host,
            start=self.tzdatetime(2032, 9, 13, 12, 0),
        )
        self.assertFalse(entry.is_finished)
        return entry

    def _schedule(self, customer=None):
        if customer is None:
            customer = self.c.customer
        hat = SortingHat(
            customer=customer,
            lesson_type=self.lesson.get_contenttype().pk,
            teacher=self.entry.teacher,
            date=self.entry.start.strftime('%Y-%m-%d'),
            time=self.entry.start.strftime('%H:%M'),
        )
        result = hat.do_the_thing()
        print(hat.err)
        self.assertTrue(result, "Cant schedule a lesson!")
        hat.c.save()

    def test_originator_timestamp_entries_class(self):
        ev = AccEvent(
            teacher=self.host,
            originator=self.entry,
            event_type='class',
        )
        ev.save()

        self.assertEqual(ev.originator_time, self.entry.start)

    def test_originator_timestamp_entries_cancellation(self):
        ev = AccEvent(
            teacher=self.host,
            originator=self.c,
            event_type='customer_inspired_cancellation',
        )
        ev.save()

        self.assertEqual(ev.originator_time, ev.timestamp)

    def test_originator_customers_cancellation(self):
        ev = AccEvent(
            teacher=self.host,
            originator=self.c,
            event_type='customer_inspired_cancellation',
        )
        ev.save()

        self.assertEqual(ev.originator_customers, [self.customer])

    def test_originator_customers_single(self):
        ev = AccEvent(
            teacher=self.host,
            originator=self.entry,
            event_type='class',
        )
        ev.save()

        self.assertEqual(ev.originator_customers[0], self.customer)

    def test_originator_customers_multiple(self):
        """
        Add a second customer to the timeline entry and check if originator_customer
        will return it.
            1) set slot count of a lesson to 5
            2) update the timeline entry (calling save()) to set it's slot count
            3) schedule a class of another customer
            4) ???
            5) check originator_customers

        """
        self.lesson.slots = 5  # set lesson slots to 5, to update timeine entry slot count
        self.lesson.save()
        self.entry.save()

        other_customer = create_customer()

        self._buy_a_lesson(customer=other_customer)
        self._schedule(customer=other_customer)

        ev = AccEvent(
            teacher=self.host,
            originator=self.entry,
            event_type='class',
        )
        ev.save()

        self.assertEqual(len(ev.originator_customers), 2)
        self.assertIn(other_customer, ev.originator_customers)
        self.assertIn(self.customer, ev.originator_customers)
