from unittest.mock import patch

from django.core.exceptions import ObjectDoesNotExist

from accounting.models import Event as AccEvent
from accounting.tasks import bill_timeline_entries
from elk.utils.testing import ClassIntegrationTestCase


class TestClassIntegration(ClassIntegrationTestCase):
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
    fixtures = ('lessons',)

    @patch('timeline.models.EntryManager._EntryManager__now')
    def test_class_marked_as_used(self, now):
        c = self._buy_a_lesson()
        entry = self._create_entry()

        self._schedule(c, entry)

        c.refresh_from_db()
        self.assertTrue(c.is_scheduled)

        now.return_value = self.tzdatetime(2032, 9, 13, 15, 0)

        with patch('timeline.models.Entry.clean') as clean:
            clean.return_value = True
            bill_timeline_entries()

        with self.assertRaises(ObjectDoesNotExist):
            entry.refresh_from_db()

        c.refresh_from_db()
        self.assertTrue(c.is_fully_used)

        self.assertEqual(AccEvent.objects.count(), 1)
