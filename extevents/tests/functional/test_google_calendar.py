from unittest.mock import MagicMock

from extevents.models import ExternalEvent
from extevents.tests import GoogleCalendarTestCase


class TestGoogleCalendar(GoogleCalendarTestCase):
    def test_event_saving(self):
        self.src.fetch_calendar = MagicMock(
            return_value=self.read_fixture('simple-plus-recurring.ics')
        )

        self.src.poll()

        """
        1 event from 2032
        1 event from 2016 — the root of recurring events
        8 events generated in 8 weeks from 2023
        """
        assumed_events_count = 1 + 1 + self.src.EXTERNAL_EVENT_WEEK_COUNT

        self.assertEqual(len(self.src.events), assumed_events_count)

        self.src.update()

        loaded_event_count = ExternalEvent.objects.all().count()
        self.assertEqual(loaded_event_count, assumed_events_count)

    def test_repeated_event_saving(self):
        """
        Try to save to identical events — nothing should fail
        """
        self.src.fetch_calendar = MagicMock(
            return_value=self.read_fixture('event-overlap.ics')
        )

        self.src.poll()

        self.assertEqual(len(self.src.events), 2)

        self.src.update()
        loaded_event_count = ExternalEvent.objects.all().count()
        self.assertEqual(loaded_event_count, 2)
