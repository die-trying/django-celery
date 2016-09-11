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
        return open('./extevents/fixtures/google.ics', 'r').read()

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

    def test_parse_calendar(self):
        self.src.parse_calendar(self.__fixtured_calendar())

        self.assertEqual(len(self.src.events), 8)

        ev = self.src.events[0]
        self.assertIsInstance(ev, models.ExternalEvent)

        # self.assertEqual(ev.description, 'testev')
        # self.assertEqual(ev.start, self.tzdatetime('Europe/Moscow', 2016, 9, 10, 16, 0))
        # self.assertEqual(ev.end, self.tzdatetime('Europe/Moscow', 2016, 9, 10, 17, 0))

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
