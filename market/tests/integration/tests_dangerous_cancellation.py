from django.core.exceptions import ObjectDoesNotExist
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import ClassIntegrationTestCase, create_customer
from lessons import models as lessons
from market.exceptions import CannotBeUnscheduled


class TestDangerousUnschedule(ClassIntegrationTestCase):
    def test_single_class(self):
        """
        1. Buy a class
        2. Schedule it
        3. Move to the future
        4. Assure it is not cancellable in the normal way
        5. Dangerously_unshedule() it
        6. Check if timeline entry is cancelled too
        """
        entry = self._create_entry()
        c = self._buy_a_lesson()
        self._schedule(c, entry)

        with freeze_time('2032-09-15 15:00'):  # now entry is in past
            with self.assertRaises(CannotBeUnscheduled):
                c.unschedule()

            c.dangerously_unschedule()

            with self.assertRaises(ObjectDoesNotExist):  # timeline entry should be dropped now
                entry.refresh_from_db()

            c.refresh_from_db()

            self.assertFalse(c.is_scheduled)
            self.assertFalse(c.is_fully_used)

    def test_multiple_classes(self):
        """
        1. Buy two classes
        2. Schedule both of them for single timeline entry with 5 slots.
        3. Move to the future
        4. Assure it is not cancellable in the normal way
        5. Dangerously_unschedule() it
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
            with self.assertRaises(CannotBeUnscheduled):
                c.unschedule()
            c.dangerously_unschedule()

            entry.refresh_from_db()
            self.assertEqual(entry.taken_slots, 1)
