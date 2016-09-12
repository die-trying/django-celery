import datetime
from unittest.mock import MagicMock

from elk.utils.testing import TestCase, create_teacher
from extevents import models


class TestGoogleCalendar(TestCase):
    def setUp(self):
        self.teacher = create_teacher()
        self.src = models.GoogleCalendar(
            teacher=self.teacher,
            url='http://testing'
        )
        self.src.save()

    def __fixtured_calendar(self):
        return str(open('./extevents/fixtures/google.ics', 'r').read())

    def __fake_event(self, start, end):
        """
        Create a mocked calendar event
        """
        event = MagicMock()

        def fake_param(name):
            if name == 'dtstart':
                time = MagicMock()
                time.dt = start
                return time
            if name == 'dtend':
                time = MagicMock()
                time.dt = end
                return time

        event.get = fake_param

        return event

    def test_poll(self):
        """
        Test for the poll method to actualy parse the events.
        """
        self.src.fetch_calendar = MagicMock(return_value=self.__fixtured_calendar())

        fake_event = MagicMock()
        fake_event.start = self.tzdatetime('Europe/Moscow', 2011, 1, 1, 12, 1)

        fake_event_parser = MagicMock()
        fake_event_parser.return_value = fake_event

        self.src.parse_event = fake_event_parser

        self.src.poll()

        self.assertEqual(fake_event_parser.call_count, 6)  # make sure that poll has parsed 6 events

    def test_parse_calendar(self):
        events = [ev for ev in self.src.parse_events(self.__fixtured_calendar())]

        self.assertEqual(len(events), 1)

        ev = events[0]
        self.assertIsInstance(ev, models.ExternalEvent)

        self.assertEqual(ev.description, 'far-event')
        self.assertEqual(ev.start, self.tzdatetime('Europe/Moscow', 2032, 9, 11, 21, 0))
        self.assertEqual(ev.end, self.tzdatetime('Europe/Moscow', 2032, 9, 11, 22, 0))

    def test_event_time_normal(self):
        start = self.tzdatetime('Europe/Moscow', 2016, 9, 10, 16, 0)
        end = self.tzdatetime('Europe/Moscow', 2016, 9, 10, 16, 0)

        event = self.__fake_event(start, end)

        (a, b) = self.src._GoogleCalendar__event_time(event)

        self.assertEqual(a, start)
        self.assertEqual(b, end)

    def test_event_time_whole_day(self):
        start = datetime.date(2016, 12, 5)
        event = self.__fake_event(start, start)

        (a, b) = self.src._GoogleCalendar__event_time(event)

        self.assertEqual(a, self.tzdatetime('UTC', 2016, 12, 5, 0, 0))
        self.assertEqual(b, self.tzdatetime('UTC', 2016, 12, 5, 0, 0))
