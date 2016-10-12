from unittest.mock import patch

from django.core.exceptions import ObjectDoesNotExist
from freezegun import freeze_time
from mixer.backend.django import mixer

from accounting.models import Event as AccEvent
from accounting.tasks import bill_timeline_entries
from elk.utils.testing import ClassIntegrationTestCase, create_customer
from lessons import models as lessons


class TestDangerousUnschedule(ClassIntegrationTestCase):
    @patch('timeline.models.Entry.clean')
    def test_accounting_single_record_removal(self, clean):
        """
        1. Buy a class
        2. Schedule it
        3. Move to the future
        4. Account it
        5. Dangerously_cancel() it
        6. Check if account record has gone
        """
        clean.return_value = True

        entry = self._create_entry()
        c = self._buy_a_lesson()
        self._schedule(c, entry)

        entry = c.timeline  # get a new timeline entry

        with freeze_time('2032-09-15 15:00'):  # now entry is in past
            bill_timeline_entries()
            ev = AccEvent.objects.by_originator(entry).first()
            self.assertIsNotNone(ev)

            entry.delete(src='dangerous-cancellation')
            with self.assertRaises(ObjectDoesNotExist):
                ev.refresh_from_db()  # the accounting event should be dropped while unscheduling the last class

            c.refresh_from_db()
            self.assertFalse(c.is_scheduled)
            self.assertFalse(c.is_fully_used)

    def test_multiple_classes(self):
        """
        The same as above but with two classes to check how account record deletion works
        when entry autodeletion is not invoked.
        """
        self.lesson = mixer.blend(lessons.MasterClass, host=self.host, slots=5)
        entry = self._create_entry()

        entry.slots = 5
        entry.save()

        c = self._buy_a_lesson()
        self._schedule(c, entry)

        self.customer = create_customer()  # create another customer
        c1 = self._buy_a_lesson()
        self._schedule(c1, entry)
        entry.refresh_from_db()  # we have the same entry here because the lesson is hosted

        with freeze_time('2032-09-15 15:00'):  # now entry is in past
            bill_timeline_entries()
            ev = AccEvent.objects.by_originator(entry).first()
            self.assertIsNotNone(ev)

            entry.delete(src='dangerous-cancellation')

            with self.assertRaises(ObjectDoesNotExist):
                ev.refresh_from_db()  # the accounting event should be dropped while unscheduling the last class

            c.refresh_from_db()
            c1.refresh_from_db()

            self.assertFalse(c.is_scheduled)
            self.assertFalse(c.is_fully_used)
            self.assertFalse(c1.is_scheduled)
            self.assertFalse(c1.is_fully_used)

    def test_one_of_multiple_classes(self):
        """
        1. Buy two classes
        2. Schedule both of them for single timeline entry with 5 slots.
        3. Move to the future
        4. Assure it is not cancellable in the normal way
        5. Dangerously_unschedule() on of them
        6. Check if timeline entry has only one remaining slot
        """
        self.lesson = mixer.blend(lessons.MasterClass, host=self.host, slots=5)
        entry = self._create_entry()

        entry.slots = 5
        entry.save()

        c = self._buy_a_lesson()
        self._schedule(c, entry)

        self.customer = create_customer()  # create another customer
        c1 = self._buy_a_lesson()
        self._schedule(c1, entry)

        with freeze_time('2032-09-15 15:00'):  # now entry is in past
            c.cancel(src='dangerous-cancellation')
            entry.refresh_from_db()
            self.assertEqual(entry.taken_slots, 1)
