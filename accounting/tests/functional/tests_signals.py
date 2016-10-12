from accounting.models import Event as AccEvent
from elk.utils.testing import ClassIntegrationTestCase


class TestClassCancellation(ClassIntegrationTestCase):
    def test_customer_class_cancellation(self):
        c = self._buy_a_lesson()
        entry = self._create_entry()

        self._schedule(c, entry)

        c.cancel(src='customer')

        event = AccEvent.objects.by_originator(originator=c).filter(event_type='customer_inspired_cancellation').first()
        self.assertIsNotNone(event)

    def test_teacher_class_cancellation(self):
        c = self._buy_a_lesson()
        entry = self._create_entry()

        self._schedule(c, entry)

        c.cancel()  # with default src

        event = AccEvent.objects.by_originator(originator=c).filter(event_type='customer_inspired_cancellation').first()
        self.assertIsNone(event)

    def test_five_times_class_cancellation(self):
        """
        If we schedule and cancel a class 5 times in a row, that should cause 5
        accounting recors
        """

        c = self._buy_a_lesson()

        for i in range(0, 5):
            entry = self._create_entry()
            self._schedule(c, entry)
            c.cancel(src='customer')

        events = AccEvent.objects.by_originator(originator=c).filter(event_type='customer_inspired_cancellation')

        self.assertEqual(events.count(), 5)
