import datetime
from unittest.mock import MagicMock, patch

from icalendar import Calendar

import extevents.models as models
from extevents.tests import GoogleCalendarTestCase


class TestGoogleCalendar(GoogleCalendarTestCase):
    def test_poll(self):
        """
        Test for the poll method to actualy parse the events.
        """
        self.src.fetch_calendar = MagicMock(return_value=self.read_fixture('simple.ics'))

        fake_event = MagicMock()
        fake_event.start = self.tzdatetime('Europe/Moscow', 2011, 1, 1, 12, 1)

        fake_event_parser = MagicMock()
        fake_event_parser.return_value = fake_event

        self.src.parse_event = fake_event_parser

        self.src.poll()

        self.assertEqual(fake_event_parser.call_count, 5)  # make sure that poll has parsed 5 events

    @patch('extevents.models.Calendar')
    def test_value_error(self, Calendar):
        """ Should not throw anything when ical raiss ValueError """
        Calendar = MagicMock()
        Calendar.from_ical = MagicMock(side_effect=ValueError)
        res = list(self.src.parse_events('sdfsdf'))
        self.assertEqual(res, [])

    def test_parse_calendar(self):
        """
        Parse events from the default fixture.
        """
        events = list(self.src.parse_events(self.read_fixture('simple.ics')))  # read and parse the 'simple.ics' fixture

        self.assertEqual(len(events), 1)  # there is one one actual event dated 2032 year. All others are in the past.

        ev = events[0]
        self.assertIsInstance(ev, models.ExternalEvent)

        self.assertEqual(ev.description, 'far-event')
        self.assertEqual(ev.start, self.tzdatetime('Europe/Moscow', 2032, 9, 11, 21, 0))
        self.assertEqual(ev.end, self.tzdatetime('Europe/Moscow', 2032, 9, 11, 22, 0))

    def test_simple_events_ignores_recurring_events(self):
        ical = Calendar.from_ical(self.read_fixture('recurring.ics'))
        events = list(self.src._GoogleCalendar__simple_events(ical))
        self.assertEqual(len(events), 0)  # this test will fail in 2023, see fixtures/recurring.ics:19

    @patch('extevents.models.timezone')
    def test_recurring_events_count(self, timezone):
        timezone.now = MagicMock(return_value=self.tzdatetime('UTC', 2023, 9, 11, 10, 0))
        ical = Calendar.from_ical(self.read_fixture('recurring.ics'))
        events = list(self.src._GoogleCalendar__recurring_events(ical))
        self.assertEqual(len(events), self.src.EXTERNAL_EVENT_WEEK_COUNT + 1)  # weekly event should repeat as many times as recurring is configured

    @patch('extevents.models.timezone')
    def test_recurring_events_are_the_same(self, timezone):
        """
        All generated events should be the same besides the length
        """
        timezone.now = MagicMock(return_value=self.tzdatetime('UTC', 2023, 9, 11, 10, 0))
        ical = Calendar.from_ical(self.read_fixture('recurring.ics'))

        for ev in self.src._GoogleCalendar__recurring_events(ical):
            self.assertIsInstance(ev, models.ExternalEvent)
            self.assertEqual(ev.end - ev.start, datetime.timedelta(hours=1))  # all generated events should have similar length
            self.assertEqual(ev.src, self.src)

    @patch('extevents.models.timezone')
    def test_simple_and_recurring_events_mixup(self, timezone):
        timezone.now = MagicMock(return_value=self.tzdatetime('UTC', 2023, 9, 11, 10, 0))
        events = list(self.src.parse_events(self.read_fixture('simple-plus-recurring.ics')))  # read and parse the 'simple.ics' fixture

        """
        1 event from 2032
        1 event from 2016 — the root of recurring events
        8 events generated in 8 weeks from 2023
        """
        assumed_event_count = 1 + 1 + self.src.EXTERNAL_EVENT_WEEK_COUNT

        self.assertEqual(len(events), assumed_event_count)

    def test_event_time_normal(self):
        start = self.tzdatetime('Europe/Moscow', 2016, 9, 10, 16, 0)
        end = self.tzdatetime('Europe/Moscow', 2016, 9, 10, 16, 0)

        event = self.fake_event(start, end)

        (a, b) = self.src._GoogleCalendar__event_time(event)

        self.assertEqual(a, start)
        self.assertEqual(b, end)

    def test_event_time_whole_day(self):
        """
        Test case for fixing icalendar type strange behaviour: for the whole-day
        events it returns an instance of `datetime.date` instead of `datetime.datetime`.
        Datetime.date is not a usable datetime, because all dates in the app
        are of `datetime.datetime` type.
        """
        start = datetime.date(2016, 12, 5)
        event = self.fake_event(start, start)

        (a, b) = self.src._GoogleCalendar__event_time(event)

        self.assertEqual(a, self.tzdatetime('UTC', 2016, 12, 5, 0, 0))
        self.assertEqual(b, self.tzdatetime('UTC', 2016, 12, 5, 23, 59, 59, 999999))
