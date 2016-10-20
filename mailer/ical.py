from urllib.parse import urlparse

import icalendar
from django.conf import settings


class Ical():
    def __init__(self, start, end, summary, uid):

        self.start = start
        self.end = end
        self.summary = summary
        self.uid = uid

        self.calendar = self._build()

    def _build(self):
        calendar = self._calendar_boilerplate()
        calendar.add_component(self._event())

        return calendar

    def as_string(self):
        return self.calendar.to_ical().decode('utf-8')

    def _calendar_boilerplate(self):
        calendar = icalendar.Calendar()
        calendar.add('method', 'request')

        return calendar

    def _event(self):
        event = self._event_boilerplate()
        event.add('dtstart', self.start)
        event.add('dtend', self.end)
        event.add('summary', self.summary)

        return event

    def _event_boilerplate(self):
        event = icalendar.Event()
        event.add('uid', self.__uid())
        event.add('ogranizer', self.__organizer())

        return event

    def __uid(self):
        return '{uid}@{host}'.format(
            uid=self.uid,
            host=urlparse(settings.ABSOLUTE_HOST).netloc,
        )

    def __organizer(self):
        return icalendar.vCalAddress('MAILTO:%s' % settings.SUPPORT_EMAIL)
