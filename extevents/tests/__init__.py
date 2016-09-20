from elk.utils.testing import TestCase, create_teacher
from unittest.mock import MagicMock
from os.path import join

import extevents.models as models


class GoogleCalendarTestCase(TestCase):
    """
    Generic case for testing external event sources. It incapsulates an instance
    of :model:`extevents.GoogleCalendar` and provides method to read calendars
    from fixtures and to mock calendar events.
    """
    def setUp(self):
        self.teacher = create_teacher()
        self.src = models.GoogleCalendar(
            teacher=self.teacher,
            url='http://testing'
        )
        self.src.save()

    def read_fixture(self, src):
        """
        Read an .ICS file and return it's content
        """
        src = join('./extevents/fixtures/', src)

        return str(open(src, 'r').read())

    def fake_event(self, start, end):
        """
        Create a mocked calendar event
        """
        event = MagicMock()

        def fake_param(name):
            """
            Fake an icalendar event parameter.
            """
            param = MagicMock()

            if name == 'dtstart':
                param.dt = start
            if name == 'dtend':
                param.dt = end

            return param
        event.get = fake_param

        return event
