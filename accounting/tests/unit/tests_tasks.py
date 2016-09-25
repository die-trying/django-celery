from unittest.mock import MagicMock, patch

from mixer.backend.django import mixer

from accounting.models import Event as AccEvent
from accounting.tasks import bill_timeline_entries
from elk.utils.testing import TestCase, create_teacher
from timeline.models import Entry as TimelineEntry


class TestBillTimelineEntries(TestCase):
    def setUp(self):
        self.teacher = create_teacher()
        self.entry = mixer.blend(
            TimelineEntry,
            teacher=self.teacher,
            start=self.tzdatetime(2032, 5, 10, 21, 0),
            is_finished=False,
        )

    @patch('timeline.models.EntryManager._EntryManager__now')
    def test_timeline_entry_marking(self, now):
        now.return_value = self.tzdatetime(2032, 5, 11)
        bill_timeline_entries()
        self.entry.refresh_from_db()

        self.assertTrue(self.entry.is_finished)

    @patch('timeline.models.EntryManager._EntryManager__now')
    def test_event_creation(self, now):
        now.return_value = self.tzdatetime(2032, 5, 11)

        self.assertEqual(AccEvent.objects.count(), 0)
        bill_timeline_entries()
        self.assertEqual(AccEvent.objects.count(), 1)

    @patch('timeline.models.EntryManager._EntryManager__now')
    def test_bypass_already_billed_originators(self, now):
        now.return_value = self.tzdatetime(2032, 5, 11)

        bill_timeline_entries()

        self.entry.is_finished = False
        self.entry.save()
        bill_timeline_entries()
        self.assertEqual(AccEvent.objects.count(), 1)

        ev = AccEvent.objects.all()[0]
        self.assertEqual(ev.event_type, 'class')

    @patch('timeline.models.EntryManager._EntryManager__now')
    def test_warn_logging(self, now):
        now.return_value = self.tzdatetime(2032, 5, 11)

        bill_timeline_entries()

        self.entry.is_finished = False
        self.entry.save()
        with patch('accounting.tasks.logger') as logger:
            logger.warning = MagicMock()
            bill_timeline_entries()

            self.assertEqual(logger.warning.call_count, 1)
