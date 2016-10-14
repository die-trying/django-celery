
from django.core.exceptions import ObjectDoesNotExist
from freezegun import freeze_time

from accounting.models import Event as AccEvent
from accounting.tasks import bill_timeline_entries
from elk.utils.testing import ClassIntegrationTestCase


@freeze_time('2032-09-13 20:00')
class TestAccountingEventIntegration(ClassIntegrationTestCase):
    """
    Big integration test:
        — Buy a lesson
        — Create a timeline entry for the teacher
        — Schedule this lesson
        — Wait until it's passed
        — ???
        — Check if entry is marked as finished
        — Check if class is marked as used
        — Check if billing event created
    """

    def test_class_marked_as_used(self):
        c = self._buy_a_lesson()
        entry = self._create_entry()

        self._schedule(c, entry)

        c.refresh_from_db()
        self.assertTrue(c.is_scheduled)

        bill_timeline_entries()  # run the periodic task by hand

        with self.assertRaises(ObjectDoesNotExist):
            entry.refresh_from_db()

        c.refresh_from_db()
        self.assertTrue(c.is_fully_used)

        self.assertEqual(AccEvent.objects.count(), 1)
