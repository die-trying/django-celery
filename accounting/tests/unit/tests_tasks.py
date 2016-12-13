from unittest.mock import MagicMock, patch

from freezegun import freeze_time
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
            taken_slots=1,
            teacher=self.teacher,
            start=self.tzdatetime(2032, 5, 10, 21, 0),
            is_finished=False,
        )

    @freeze_time('2032-05-11')
    def test_timeline_entry_marking(self):
        bill_timeline_entries()
        self.entry.refresh_from_db()

        self.assertTrue(self.entry.is_finished)

    @freeze_time('2032-05-11')
    def test_event_creation(self):
        self.assertEqual(AccEvent.objects.count(), 0)
        bill_timeline_entries()
        self.assertEqual(AccEvent.objects.count(), 1)

    def test_bypass_already_billed_originators(self):
        bill_timeline_entries()

        self.entry.is_finished = False
        self.entry.save()
        bill_timeline_entries()
        self.assertEqual(AccEvent.objects.count(), 1)

        ev = AccEvent.objects.all()[0]
        self.assertEqual(ev.event_type, 'class')

    @freeze_time('2032-05-11')
    def test_warn_logging(self):
        """
        Try to double-bill the same timeline entry
        """
        with patch('timeline.models.Entry._Entry__self_delete_if_needed') as self_delete:  # disable self-deletion (the entry is in past here!)
            self_delete.return_value = False

            bill_timeline_entries()

            self.entry._Entry__update_slots = MagicMock()  # disable timeslot updating — the entry needs to have slots for beeing billed
            self.entry.is_finished = False
            self.entry.save()

            with patch('accounting.tasks.logger') as logger:
                logger.warning = MagicMock()
                bill_timeline_entries()

                self.assertEqual(logger.warning.call_count, 1)
