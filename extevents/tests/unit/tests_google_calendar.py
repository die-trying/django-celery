import datetime
from unittest.mock import MagicMock, patch

import extevents.models as models
from extevents.tests import GoogleCalendarTestCase


class TestGoogleCalendar(GoogleCalendarTestCase):
    def test_poll(self):
        """
        Test for the poll method to actualy parse the events.
        """
        self.src.fetch_calendar = MagicMock(return_value=self.fixtured_calendar('./extevents/fixtures/google.ics'))

        fake_event = MagicMock()
        fake_event.start = self.tzdatetime('Europe/Moscow', 2011, 1, 1, 12, 1)

        fake_event_parser = MagicMock()
        fake_event_parser.return_value = fake_event

        self.src.parse_event = fake_event_parser

        self.src.poll()

        self.assertEqual(fake_event_parser.call_count, 6)  # make sure that poll has parsed 6 events

    @patch('extevents.models.Calendar')
    def test_value_error(self, Calendar):
        """ Should not throw anything when ical raiss ValueError """
        Calendar = MagicMock()
        Calendar.from_ical = MagicMock(side_effect=ValueError)
        res = [ev for ev in self.src.parse_events('sdfsdf')]
        self.assertEqual(res, [])

    def test_parse_calendar(self):
        """
        Parse events from the default fixture.
        """
        events = [ev for ev in self.src.parse_events(self.fixtured_calendar('./extevents/fixtures/google.ics'))]  # read and parse the 'google.ics' fixture

        self.assertEqual(len(events), 1)  # there is one one actual event dated 2032 year. All others are in the past.

        ev = events[0]
        self.assertIsInstance(ev, models.ExternalEvent)

        self.assertEqual(ev.description, 'far-event')
        self.assertEqual(ev.start, self.tzdatetime('Europe/Moscow', 2032, 9, 11, 21, 0))
        self.assertEqual(ev.end, self.tzdatetime('Europe/Moscow', 2032, 9, 11, 22, 0))

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
        self.assertEqual(b, self.tzdatetime('UTC', 2016, 12, 5, 0, 0))
